import tweetsearcher, pygame, requests, threading, StringIO, tempfile
import pygame.freetype as font
import xml.sax.saxutils as xml

white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
BORDER_WIDTH = 10
BORDER_HEIGHT = 10

class TweetViewer(threading.Thread):
        def __init__(self, searcher, size):
                threading.Thread.__init__(self)
                self.daemon = True
                self.screen = pygame.display.set_mode(size)
                self.nameFont = font.SysFont('helvetica', 20)
                self.textFont = font.SysFont('helvetica', 15)
                self.searcher = searcher
		self.tempfiles = {}
        def run(self):
                while True:
                        self.screen.fill(white)
                        with self.searcher.listLock:
                                tweetList = []
                                for tweet in self.searcher.recentList:
                                        surfaceList = []
                                        nameSurface = self.nameFont.render('@' + tweet['user']['screen_name'], blue)[0]
                                        surfaceList.append(nameSurface)
                                        text = tweet['text']
                                        entities = []
                                        if 'urls' in tweet['entities']:
                                                entities.extend([(entity, 'url') for entity in tweet['entities']['urls']])
                                        if 'media' in tweet['entities']:
                                                entities.extend([(entity, 'media') for entity in tweet['entities']['media']])
                                        entities = reversed(sorted(entities, key = lambda (entity, eType): entity['indices']))
                                        for (entity, eType) in entities:
                                                if eType == 'url':
                                                        text = text[0:entity['indices'][0]] + entity['expanded_url'] + text[entity['indices'][1]:]
                                                if eType == 'media':
                                                        text = text[0:entity['indices'][0]] + text[entity['indices'][1]:]
                                        surfaceList.extend([self.textFont.render(unicode(xml.unescape(line)), black)[0] for line in text.split('\n')])
                                        if 'media' in tweet['entities']:
                                                surfaceList.extend([self.getImage(media) for media in tweet['entities']['media'] if media['type'] == 'photo'])
                                        popSurface = self.textFont.render('Retweets: ' + str(tweet['retweet_count']) + '    ' + 'Favorites: ' + str(tweet['favorite_count']), black)[0]
                                        surfaceList.append(popSurface)
                                        tweetList.append(newTweetSurface(surfaceList))
                                blitList(self.screen, tweetList)
                                pygame.display.update()
                                self.searcher.listLock.wait()
	def getImage(self, mediaObj):
		print 'getting image'
		if mediaObj['media_url'] in self.tempfiles:
			temp = open(self.tempfiles[mediaObj['media_url']].name)
			temp.seek(0)
			return pygame.image.load(temp)
		if 'thumb' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':thumb')
		elif 'small' in mediaObj['sizes']:
			imgRequest = requests.get(mediaObj['media_url'] + ':small')
		else:
			imgRequest = requests.get(mediaObj['media_url'])
		if imgRequest.status_code == 200:
			temp = tempfile.NamedTemporaryFile(mode = 'rb+', delete = False)
			print 'image downloaded'
			temp.write(imgRequest.content)
			temp.seek(0)
			self.tempfiles[mediaObj['media_url']] = temp
			return pygame.image.load(temp)
		else:
			return None
def blitList(surface, sourceList):
        loc = [0, 0]
        addedList = []
        for source in sourceList:
                if loc[1] + source.get_height() > surface.get_height():
                        loc[1] = 0
                        loc[0] += max([s.get_width() for s in addedList])
                        addedList = []
                surface.blit(source, loc)
                loc[1] += source.get_height()
                addedList.append(source)
def newTweetSurface(surfaceList):
        tweetHeight = sum([surface.get_height() for surface in surfaceList]) + BORDER_HEIGHT
        tweetWidth = max([surface.get_width() for surface in surfaceList]) + BORDER_WIDTH
        tweetSurface = pygame.Surface((tweetWidth, tweetHeight))
        tweetSurface.fill(white)
        blitList(tweetSurface, surfaceList)
        return tweetSurface
