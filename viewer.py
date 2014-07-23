import pygame, requests, sys, json
from base64 import *
from searcher import *
from constants import *
from threading import Thread
from StringIO import StringIO
from tempfile import NamedTemporaryFile
import pygame.freetype as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
import xml.sax.saxutils as xml

#Constants
BORDER_WIDTH = 10
BORDER_HEIGHT = 10

#Takes the tweetlist from tweetsearcher, and displays it using pygame
class Viewer(Thread):
        def __init__(self, searcher, exitor):
                Thread.__init__(self)
		self.screen = pygame.Surface(SCR_SIZE)
                self.nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
                self.textFont = font.SysFont('helvetica', 15)
                self.searcher = searcher
		self.exitor = exitor
		self.tempfiles = {}#Image temp files
		self.sock = None
		self.clients = []
        #Updates screen
        def run(self):
                while True:
			with self.exitor.lock:
				if self.exitor.exited:
					for tfile in self.tempfiles.values():
						tfile.close()
					for client in self.clients:
						client.send("exit")
					sys.exit()
                        self.screen.fill(white)
                        with self.searcher.listLock:
                                tweetList = []#List of tweet surfaces, not tweets themselves
                                for tweet in self.searcher.recentList:#these are the actual tweets
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
				self.putTweetsOnScreen(tweetList)#puts all tweet surfaces on screen
				self.sendScreen()
				self.deleteUnusedTempfiles()
				self.searcher.listLock.wait()#waits until the tweet list changes
	def addClient(self, client):
		self.sock = client
		self.clients.append(client)
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
	def putTweetsOnScreen(self, tweetList):
		blitList(self.screen, tweetList)
	def sendScreen(self):
		for i in range(len(self.clients)):
			window = pygame.Surface(WIN_SIZE)
			window.blit(self.screen, (0, 0), area = pygame.Rect((i // WIN_PER_COLUMN) * WIN_WIDTH, (i % WIN_PER_COLUMN) * WIN_HEIGHT, WIN_WIDTH, WIN_HEIGHT))
			scrStr = b64encode(pygame.image.tostring(window, 'RGBA')) #I encode the string in base64 because json cannot store pure binary data
			scrSize = window.get_size()
			s = json.dumps([scrStr, scrSize])
			client = self.clients[i]
			client.send(str(len(s))) #The client can't recieve all the data in one go, so I have to tell it how much data to wait for
			client.recv(4)
			client.sendall(s)
			client.recv(4) #waiting to keep the client and server in sync
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
