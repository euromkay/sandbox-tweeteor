import imageHandler
from ConfigParser import SafeConfigParser
from rectangleHandler import *
import pygame, sys, json, threading, logging
import xml.sax.saxutils as xml
import pygame.font as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit

logging.basicConfig(filename = 'client.log', level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
config = SafeConfigParser()
config.read('client.conf')
font.init()
nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
textFont = font.SysFont('helvetica', config.getint('font', 'size'))

BORDER_WIDTH = 20
BORDER_HEIGHT = 20
white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
twitter_bg_blue = pygame.Color(154, 194, 223)
speechBubble = pygame.image.load('speech.png')

class Tweet():
    def __init__(self, json, rect = None):
        self.json = json
        self.id = self.json['id']
        self.retweet_count = self.json['retweet_count']
        self.favorite_count = self.json['favorite_count']
        self.text, self.imgs = self._expandLinks()
        if not rect:
            tweetSurface = self.getSurface()
            self.rect = tweetSurface.get_rect()
        else:
            self.rect = rect
        
    def get_rect(self):
        return self.rect
    
    #Helper method that takes a tweet, and returns the tweet text with all urls expanded (and image urls removed), along with a list of all the images
    def _expandLinks(self):
            text = self.json['text']
            imgList = []
            entities = []#List of all urls and media urls in tweet
            if 'urls' in self.json['entities']:#adds urls to entities
                    entities.extend([(entity, 'url') for entity in self.json['entities']['urls']])
            if 'media' in self.json['entities']:#adds mediau urls to entities
                    for entity in self.json['entities']['media']:
                            entities.append((entity, 'media'))
                            if entity['type'] == 'photo':
                                if 'thumb' in entity['sizes']:
                                    imgList.append(entity['media_url'] + ':thumb')
                                elif 'small' in mediaObj['sizes']:
                                    imgList.append(entity['media_url'] + ':small')
                                else:
                                    imgList.append(entity['media_url'])
            entities = reversed(sorted(entities, key = lambda (entity, eType): entity['indices']))
            for (entity, eType) in entities:#Removes media urls, and lengthens normal urls
                    if eType == 'url':
                            text = text[0:entity['indices'][0]] + entity['expanded_url'] + text[entity['indices'][1]:]
                    if eType == 'media':
                            text = text[0:entity['indices'][0]] + text[entity['indices'][1]:]
            return unicode(xml.unescape(text)), imgList

    ### New tweet surface generator ###
    def getSurface(self):
            surfList = []
            try:
                    userImage = imageHandler.getImage(self.json['user']['profile_image_url'])
                    imageSurf = pygame.transform.scale(userImage,(70,70))
                    surfList.append(imageSurf)
            except:
                    logging.debug('failed to download profile pic!')
            userName = self.json['user']['name']
            userScreenName = self.json['user']['screen_name']
            lines = self.text.split('\n')
            nameSurf = textFont.render('@' + userScreenName, 1, black)
            surfList.append(nameSurf)
            contentList = []
            for line in lines:
                    words = [Word(word) for word in line.split()]
                    wordSurfs = []
                    for word in words:
                            try:
                                    wordSurf = textFont.render(word.text + '  ', 1, word.color)
                                    wordSurfs.append(wordSurf)
                            except:
                                    logging.debug(word.text)
                    if wordSurfs == []:
                            continue
                    width = sum([wordSurf.get_width() for wordSurf in wordSurfs])
                    height = max([wordSurf.get_height() for wordSurf in wordSurfs])
                    lineSurf = pygame.Surface((width, height))
                    lineSurf.fill(white)
                    blitList(lineSurf, wordSurfs)
                    contentList.append(lineSurf)
            popularityCount = '';
            if self.favorite_count > 0:
                popularityCount += 'Favorites: ' + str(self.favorite_count) + ' '
            if self.retweet_count > 0:
                popularityCount += 'Retweets: ' + str(self.retweet_count)
            if len(popularityCount) > 0:
                popularityBar = textFont.render(popularityCount, 1, black)
            else:
                #Ensures that there is still space at the bottom if it is retweeted later
                popularityBar = textFont.render('Retweets:', 1, black)
                popularityBar.fill(white)
            contentList.append(popularityBar)
            contentList.extend([imageHandler.getImage(img) for img in self.imgs])
            width = max([x.get_width() for x in contentList])
            height = sum([x.get_height() for x in contentList])
            contentSurf = pygame.Surface((width, height))
            contentSurf.fill(white)
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
    def update(self, json):
        self.json = json
        self.retweet_count = json['retweet_count']
        self.favorite_count = json['favorite_count']
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
