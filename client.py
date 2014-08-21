from socket import *
from pygame.locals import *
from threading import Thread, Event
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from base64 import b64decode
import pygame.font as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
import xml.sax.saxutils as xml
import pygame, sys, json, threading, logging
import urllib

#Constants
BORDER_WIDTH = 20
BORDER_HEIGHT = 20
white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
twitter_bg_blue = pygame.Color(154, 194, 223)
speechBubble = pygame.image.load('speech.png')

### For use by tweet surface method ###
class Word():
	def __init__(self,text):
		self.text = text
		ttext = text[0:1]
		if ttext == '#' or ttext == '@':
			self.color = blue
		elif len(text) > 4 and text[0:4] == 'http':
			self.color = blue
		else:
			self.color = black

class Client(Thread):
	def __init__(self, address, coords, exit):
		Thread.__init__(self, name = 'Client')
		pygame.init()
                self.nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
                self.textFont = font.SysFont('helvetica', config.getint('font', 'size'))
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
			logging.debug("running")
			#Exits if window was closed
			if exit.isSet():
				self.sock.close()
				pygame.quit()
				sys.exit()
			msg = self.sock.recv(1024)
			try:
				length = int(msg)
			except:
				logging.debug(msg)
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
		blitList(self.screen, tweetList, self.window.get_height())
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
		surfList = []
		logging.debug('downloading profile pic')
		try:
			userImage = pygame.image.load(StringIO(urllib.urlopen(tweet['user']['profile_image_url']).read()))
			imageSurf = pygame.transform.scale(userImage,(70,70))
			surfList.append(imageSurf)
		except:
			logging.debug('failed to download profile pic!')
		logging.debug('done')
		userName = tweet['user']['name']
		userScreenName = tweet['user']['screen_name']
		tweetText, images = self.expandLinks(tweet)
		tweetText = unicode(xml.unescape(tweetText))
		lines = tweetText.split('\n')
		nameSurf = self.textFont.render('@' + userScreenName, 1, black)
		surfList.append(nameSurf)
		contentList = []
		for line in lines:
			words = [Word(word) for word in line.split()]
			wordSurfs = []
			for word in words:
				try:
					wordSurf = self.textFont.render(word.text + '  ', 1, word.color)
					wordSurfs.append(wordSurf)
				except:
					logging.debug(word.text)
			if wordSurfs == []:
				continue
			width = sum([wordSurf.get_width() for wordSurf in wordSurfs])
			height = max([wordSurf.get_height() for wordSurf in wordSurfs])
			lineSurf = pygame.Surface((width, height))
			lineSurf.fill(twitter_bg_blue)
			blitList(lineSurf, wordSurfs)
			contentList.append(lineSurf)
		contentList.extend(images)
		width = max([x.get_width() for x in contentList])
		height = sum([x.get_height() for x in contentList])
		contentSurf = pygame.Surface((width, height))
		contentSurf.fill(twitter_bg_blue)
		blitList(contentSurf, contentList)
		tailLength = width / 5
		width += BORDER_WIDTH + tailLength
		height += 2* BORDER_HEIGHT
		bubbleSurf = pygame.Surface((width, height))
		bubbleSurf.fill(twitter_bg_blue)
		bubbleSurf.blit(pygame.transform.scale(speechBubble,(width, height)),[0, 0])
		bubbleSurf.blit(contentSurf, [tailLength, BORDER_HEIGHT])
		surfList.append(bubbleSurf)
		width = max([x.get_width() for x in surfList])
		height = sum([x.get_height() for x in surfList])
		tweetSurf = pygame.Surface((width, height))
		tweetSurf.fill(twitter_bg_blue)
		blitList(tweetSurf, surfList)
		return tweetSurf

#Helper method for placing surfaces on a larger surface
def blitList(surface, sourceList, boundary = 0):
        loc = [0, 0]
        addedList = []#List of all surfaces in current column
        for source in sourceList:
                if loc[1] + source.get_height() > surface.get_height():#Starts new column if surfaces reach bottom of the destination surface
                        loc[1] = 0
                        loc[0] += max([s.get_width() for s in addedList])#Only make the columns as wide as needed
                        addedList = []
		if loc[0] + source.get_width() > surface.get_width():#Ignores surfaces too wide to fit in the surface, you don't want ugly half surfaces
			continue
		if boundary > 0 and (loc[1] + source.get_height()) / boundary != loc[1] / boundary:
			loc[1] += boundary - loc[1] % boundary
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
