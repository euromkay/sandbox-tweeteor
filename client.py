from socket import *
from pygame.locals import *
from threading import Thread, Event
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from base64 import b64decode
import pygame.freetype as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
import xml.sax.saxutils as xml
import pygame, sys, json, threading, logging
import urllib

#Constants
BORDER_WIDTH = 10
BORDER_HEIGHT = 10
white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
twitter_bg_blue=pygame.Color(154, 194, 223)
speechBubble=pygame.image.load('speech.png')

### For use by tweet surface method ###
class Word():
	def __init__(self,text):
		self.text=text
		ttext=text[0:1]
		if ttext=='#' or ttext=='@':
			self.color=blue
		elif len(text)>4 and text[0:4]=='http':
			self.color=blue
		else:
			self.color=black

class Client(Thread):
	def __init__(self, address, coords, exit):
		Thread.__init__(self, name = 'Client')
		pygame.init()
                self.nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
                self.textFont = font.SysFont('helvetica', 15)
		self.coords = self.x, self.y = coords
		self.imgs = {} #All the images, represented as strings, indexed by url
		self.imgInUse = {}
		self.exit = exit
		self.sock = socket()
		self.sock.connect(address)
		self.window = pygame.display.set_mode(json.loads(self.sock.recv(128))) #This represents the window belonging to the client
		self.sock.send('ACK')
		self.screen = pygame.Surface(json.loads(self.sock.recv(128))) #This represents the whole screen (all the clients' windows together)
		self.sock.send('ACK')
	def run(self):
		while True:
			#Exits if window was closed
			if exit.isSet():
				self.sock.close()
				pygame.quit()
				sys.exit()
			msg = self.sock.recv(1024)
			length = int(msg)
			self.sock.send('ACK') #Tells server that it got the length
			s = self.sock.recv(2048)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(2048)
			self.sock.send('done')
			s = s[0:length]#cut off the extra bytes
			if s == 'exit':
				self.sock.close()
				exit.set()
				return
			self.window.fill(white)
			tweets , imgs = json.loads(s)
			for key in imgs:
				imgs[key] = b64decode(imgs[key])
			self.imgs.update(imgs)
			tweetList = []#List of tweet surfaces, not tweets themselves
			for tweet in tweets:#these are the actual tweets
				tweetList.append(self.getTweetSurface(tweet))
			self.putTweetsOnScreen(tweetList)
			self.deleteUnusedImages()
			pygame.display.update()
	#Helper method that takes a tweet, and returns the tweet text with all urls expanded (and image urls removed), along with a list of all the images
	def expandLinks(self, tweet):
		text = tweet['text']
		imgList = []
		entities = []#List of all urls and media urls in tweet
		if 'urls' in tweet['entities']:#adds urls to entities
			entities.extend([(entity, 'url') for entity in tweet['entities']['urls']])
		if 'media' in tweet['entities']:#adds mediau urls to entities
			for entity in tweet['entities']['media']:
				entities.append((entity, 'media'))
				if entity['type'] == 'photo':
					imgList.append(self.getImage(entity))
		entities = reversed(sorted(entities, key = lambda (entity, eType): entity['indices']))
		for (entity, eType) in entities:#Removes media urls, and lengthens normal urls
			if eType == 'url':
				text = text[0:entity['indices'][0]] + entity['expanded_url'] + text[entity['indices'][1]:]
			if eType == 'media':
				text = text[0:entity['indices'][0]] + text[entity['indices'][1]:]
		return text, imgList
        #Helper method for loading images
	def getImage(self, mediaObj):
		s = self.imgs[mediaObj['media_url']]
		self.imgInUse[mediaObj['media_url']] = True
		f = StringIO(s)
		return pygame.image.load(f)
	#Placeholder method so you can change how the tweets are put on the screen(e.g. moving)
	def putTweetsOnScreen(self, tweetList):
		self.screen.fill(twitter_bg_blue)
		blitList(self.screen, tweetList)
		width, height = self.window.get_width(), self.window.get_height()
		self.window.blit(self.screen, (0, 0), area = pygame.Rect(self.coords[0] * width, self.coords[1] * height, width, height))
	def deleteUnusedImages(self):
		deletedKeys = []
		for key in self.imgs:
			if not self.imgInUse[key]:
				deletedKeys.append(key)
			self.imgInUse[key]= False
		for key in deletedKeys:
			del self.imgs[key]#Removing file from list
	### New tweet surface generator ###
	def getTweetSurface(self, tweet):
		userImage=pygame.image.load(StringIO(urllib.urlopen(tweet['user']['profile_image_url']).read()))
		userName=tweet['user']['name']
		userScreenName=tweet['user']['screen_name']
		tweetText,images=self.expandLinks(tweet)
		words= [Word(word) for word in tweetText.split()]
		tmpFont=font.SysFont('helvetica', 15)
		if images:
			coords1=(550,170)
			coords2=(450,170)
			coords3=[100,0]
			lenInit=185
			lenLast=385
		else:
			coords1=(410,125)
			coords2=(280,125)
			coords3=[130,0]
			lenInit=175
			lenLast=405
		tweetSurf=pygame.Surface(coords1)
		tweetSurf.fill(twitter_bg_blue)
		tweetSurf.blit(pygame.transform.scale(speechBubble,coords2),coords3)
		tweetSurf.blit(pygame.transform.scale(userImage,(70,70)),[15,30])
		tweetSurf.blit(tmpFont.render(userName, black)[0],[5,10])
		tweetSurf.blit(tmpFont.render('@'+userScreenName, black)[0],[5,105])
		lengthSoFar=lenInit
		heightCur=10
		for word in words:
			while '\n' in word.text:
				word.text=word.text.replace('\n','')
			while '&amp;' in word.text:
				word.text=word.text.replace('amp;','')
			tmpTweetSurf=tmpFont.render(word.text+'  ', word.color)[0]
			if lengthSoFar+tmpTweetSurf.get_width()>lenLast:
				heightCur+=tmpTweetSurf.get_height()
				lengthSoFar=lenInit
			tweetSurf.blit(tmpTweetSurf,[lengthSoFar,heightCur])
			lengthSoFar+=tmpTweetSurf.get_width()
		for image in images:
			tweetSurf.blit(pygame.transform.scale(image,(150,150)),[385,10])
		return tweetSurf

#Helper method for placing surfaces on a larger surface
def blitList(surface, sourceList):
        loc = [0, 0]
        addedList = []#List of all surfaces in current column
        for source in sourceList:
                if loc[1] + source.get_height() > surface.get_height():#Starts new column if surfaces reach bottom of the destination surface
                        loc[1] = 0
                        loc[0] += max([s.get_width() for s in addedList])#Only make the columns as wide as needed
                        addedList = []
		if loc[0] + source.get_width() > surface.get_width():#Ignores surfaces too wide to fit in the surface, you don't want ugly half surfaces
			continue
                surface.blit(source, loc)
                loc[1] += source.get_height()#move down a "row"
                addedList.append(source)

logging.basicConfig(filename = 'client.log', level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
config = SafeConfigParser()
config.read('client.conf')
address = (config.get('connection', 'address'), config.getint('connection', 'port'))
#Uses coords from file if in auto mode, otherwise asks user for coords
if config.getboolean('coordinates', 'auto'):
	coords = (config.getint('coordinates', 'x'), config.getint('coordinates', 'y'))
else:
	coords = (int(raw_input('X: ')), int(raw_input('Y: ')))
exit = Event() #Event for coordinating shutdown
client = Client(address, coords, exit)
client.start()
while True:
	#Exits if Client thread already exited
	if exit.isSet():
		pygame.quit()
		sys.exit()
	#Exits if window was closed, and tells Client thread to close
	for event in pygame.event.get():
		if event.type == QUIT:
			exit.set()
			break
	#This else block executes as long as the for loop did not break (the program is not shutting down)
	else:
		pygame.time.wait(10)
		continue
	break #Only executes if earlier break was called
