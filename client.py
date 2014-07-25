from socket import *
from pygame.locals import *
from constants import *
from threading import Thread, Event
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from tempfile import NamedTemporaryFile
import pygame.freetype as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
import xml.sax.saxutils as xml
import pygame, sys, json, threading, requests, logging

logging.basicConfig(filename = 'client.log', level=logging.DEBUG, format='[%(levelname)s] (%(threadName)s) %(message)s')
config = SafeConfigParser()
config.read('server.conf')
#Constants- DO NOT EDIT! change server.conf instead
BORDER_WIDTH = 10
BORDER_HEIGHT = 10
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = config.getint('window', 'width'), config.getint('window', 'height')
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_SIZE = SCR_WIDTH, SCR_HEIGHT = WIN_WIDTH * WIN_PER_ROW, WIN_HEIGHT * WIN_PER_COLUMN
class Client(Thread):
	def __init__(self, address, coords, exit):
		Thread.__init__(self, name = 'Client')
		pygame.init()
                self.nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
                self.textFont = font.SysFont('helvetica', 15)
		self.tempfiles = {}#Image temp files
		self.coords = self.x, self.y = coords
		self.sock = socket()
		self.sock.connect(address)
		self.screen = pygame.display.set_mode(json.loads(self.sock.recv(128))) #Gets the window size from the server
		self.exit = exit
	def run(self):
		while True:
			#Exits if window was closed
			if exit.isSet():
				self.sock.close()
				pygame.quit()
				sys.exit()
			msg = self.sock.recv(1024)
			#Exits if server tells client to close. That makes two ways to close the client
			if msg[0:4] == 'exit':
				self.sock.close()
				exit.set()
				return
			length = int(msg)
			self.sock.send('ACK') #Tells server that it got the length
			s = self.sock.recv(2048)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(2048)
			self.sock.send('done')
			s = s[0:length]#cut off the extra bytes
			self.screen.fill(white)
			tweets = json.loads(s)
			tweetList = []#List of tweet surfaces, not tweets themselves
			for tweet in tweets:#these are the actual tweets
				surfaceList = []#surfaces that make up the tweet surface
				nameSurface = self.nameFont.render('@' + tweet['user']['screen_name'], blue)[0]
				surfaceList.append(nameSurface)
				text, images = self.expandLinks(tweet)
				surfaceList.extend([self.textFont.render(unicode(xml.unescape(line)), black)[0] for line in text.split('\n')])#unescapes characters so they appear right, and splits multiline tweets into multiple lines
				if images != []:
					surfaceList.extend(images)
				popSurface = self.textFont.render('Retweets: ' + str(tweet['retweet_count']) + '    ' + 'Favorites: ' + str(tweet['favorite_count']), black)[0]
				surfaceList.append(popSurface)
				tweetList.append(newTweetSurface(surfaceList))
			self.putTweetsOnScreen(tweetList)
			self.deleteUnusedTempfiles()
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
		if mediaObj['media_url'] in self.tempfiles:#Loads pre-downloaded images from tempfiles
			temp = self.tempfiles[mediaObj['media_url']]
			temp.seek(0)
			temp.inUse = True
			return pygame.image.load(StringIO(temp.read()))#I use StringIO to stop pygame from closing the tempfile
		#For images not already downloaded, gets smallest size possible
		if 'thumb' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':thumb')
		elif 'small' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':small')
		else:
			imgRequest = requests.get(mediaObj['media_url'])
		if imgRequest.status_code == 200:#make sure the link worked
			temp = NamedTemporaryFile()
			temp.write(imgRequest.content)#Saves image in temp file so it only has to be downloaded once
			temp.seek(0)#moves to start of file
			temp.inUse = True
			self.tempfiles[mediaObj['media_url']] = temp 
			return pygame.image.load(StringIO(temp.read()))#I use StringIO to stop pygame from closing the tempfile
		else:
			return None#Not sure what happens if this is actually returned
	#Placeholder method so you can change how the tweets are put on the screen(e.g. moving)
	def putTweetsOnScreen(self, tweetList):
		entireScr = pygame.Surface(SCR_SIZE)
		entireScr.fill(white)
		blitList(entireScr, tweetList)
		self.screen.blit(entireScr, (0, 0), area = pygame.Rect(self.coords[0] * WIN_WIDTH, self.coords[1] * WIN_HEIGHT, WIN_WIDTH, WIN_HEIGHT))
	#Helper method to clear out images that aren't needed
	def deleteUnusedTempfiles(self):
		deletedKeys = []
		tempList = iter(self.tempfiles)
		for key in tempList:
			if not self.tempfiles[key].inUse:
				self.tempfiles[key].close()#Tempfiles are deleted when closed
				deletedKeys.append(key)
			self.tempfiles[key].inUse = False
		for key in deletedKeys:
			del self.tempfiles[key]#Removing file from list
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
#Helper method for making a tweet surface
def newTweetSurface(surfaceList):
        tweetHeight = sum([surface.get_height() for surface in surfaceList]) + BORDER_HEIGHT#Tweet surface is tall enough to fit all elements in one column, with border
        tweetWidth = max([surface.get_width() for surface in surfaceList]) + BORDER_WIDTH#Tweet surface is only as wide as widest element(plus a border)
        tweetSurface = pygame.Surface((tweetWidth, tweetHeight))
        tweetSurface.fill(white)
        blitList(tweetSurface, surfaceList)#fill that surface
        return tweetSurface

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
