import tweetsearcher, pygame, requests, threading, StringIO, tempfile
import pygame.freetype as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
import xml.sax.saxutils as xml

#Constants
white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
BORDER_WIDTH = 10
BORDER_HEIGHT = 10

#Takes the tweetlist from tweetsearcher, and displays it using pygame
class TweetViewer(threading.Thread):
        def __init__(self, searcher, size):
                threading.Thread.__init__(self)
                self.daemon = True#daemon threads close automatically when the process is finished
                self.screen = pygame.display.set_mode(size)
                self.nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
                self.textFont = font.SysFont('helvetica', 15)
                self.searcher = searcher
		self.tempfiles = {}#Image temp files
        #Updates screen
        def run(self):
                while True:
                        self.screen.fill(white)
                        with self.searcher.listLock:
                                tweetList = []#List of tweet surfaces, not tweets themselves
                                for tweet in self.searcher.recentList:#these are the actual tweets
                                        surfaceList = []#surfaces that make up the tweet surface
                                        nameSurface = self.nameFont.render('@' + tweet['user']['screen_name'], blue)[0]
                                        surfaceList.append(nameSurface)
                                        text = tweet['text']
                                        entities = []#List of all urls and media urls in tweet
                                        if 'urls' in tweet['entities']:#adds urls to entities
                                                entities.extend([(entity, 'url') for entity in tweet['entities']['urls']])
                                        if 'media' in tweet['entities']:#adds mediau urls to entities
                                                entities.extend([(entity, 'media') for entity in tweet['entities']['media']])
                                        entities = reversed(sorted(entities, key = lambda (entity, eType): entity['indices']))
                                        for (entity, eType) in entities:#Removes media urls, and lengthens normal urls
                                                if eType == 'url':
                                                        text = text[0:entity['indices'][0]] + entity['expanded_url'] + text[entity['indices'][1]:]
                                                if eType == 'media':
                                                        text = text[0:entity['indices'][0]] + text[entity['indices'][1]:]
                                        surfaceList.extend([self.textFont.render(unicode(xml.unescape(line)), black)[0] for line in text.split('\n')])#unescapes characters so they appear right, and splits multiline tweets into multiple lines
                                        if 'media' in tweet['entities']:#Gets all those nice images
                                                surfaceList.extend([self.getImage(media) for media in tweet['entities']['media'] if media['type'] == 'photo'])
                                        popSurface = self.textFont.render('Retweets: ' + str(tweet['retweet_count']) + '    ' + 'Favorites: ' + str(tweet['favorite_count']), black)[0]
                                        surfaceList.append(popSurface)
                                        tweetList.append(newTweetSurface(surfaceList))
                                blitList(self.screen, tweetList)#puts all tweet surfaces on screen
                                pygame.display.update()
                                self.searcher.listLock.wait()#waits until the tweet list changes
        #Helper method for loading images
	def getImage(self, mediaObj):
		if mediaObj['media_url'] in self.tempfiles:#Loads pre-downloaded images from tempfiles
			temp = open(self.tempfiles[mediaObj['media_url']].name)
			temp.seek(0)#Moves to start of the file, so everything is read
			return pygame.image.load(temp)
		#For images not already downloaded, gets smallest size possible
		if 'thumb' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':thumb')
		elif 'small' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':small')
		else:
			imgRequest = requests.get(mediaObj['media_url'])
		if imgRequest.status_code == 200:#make sure the link worked
			temp = tempfile.NamedTemporaryFile(mode = 'rb+', delete = False)
			temp.write(imgRequest.content)#Saves image in temp file so it only has to be downloaded once
			temp.seek(0)#moves to start of file
			self.tempfiles[mediaObj['media_url']] = temp
			return pygame.image.load(temp)
		else:
			return None#Not sure what happens if this is actually returned
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
