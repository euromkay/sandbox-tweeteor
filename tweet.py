import os
import xml.sax.saxutils as xml
from ConfigParser import SafeConfigParser

import pygame
import pygame.font as font

import image_handler
from rectangle_handler import blit_list

config = SafeConfigParser()
config.read('config')
font.init()

BORDER_WIDTH = 20
BORDER_HEIGHT = 20
WHITE = pygame.Color(255, 255, 255, 255)
BLACK = pygame.Color(0, 0, 0, 255)
BLUE = pygame.Color(0, 0, 255, 255)
TWITTER_BLUE = pygame.Color(154, 194, 223)


class Tweet(object):

    def __init__(self, json, rect=None):
        self.json = json
        self.id = self.json['id']
        self.retweet_count = self.json['retweet_count']
        self.favorite_count = self.json['favorite_count']
        self.text, self.imgs = self.expand_links()
        if not rect:
            surface = self.create_surface()
            pygame.image.save(
                surface,
                os.path.join("images", str(self.id) + ".png"))
            self.rect = surface.get_rect()
        else:
            self.rect = rect

    def get_rect(self):
        return self.rect

    def get_surface(self):
        filename = os.path.join("images", str(self.id) + ".png")
        return pygame.image.load(filename)

    def expand_links(self):
        text = self.json['text']
        imgs = []
        entities = []  # List of all urls and media urls in tweet
        if 'urls' in self.json['entities']:  # adds urls to entities
            entities.extend(
                [(entity, 'url') for entity in self.json['entities']['urls']])
        if 'media' in self.json['entities']:  # adds mediau urls to entities
            for entity in self.json['entities']['media']:
                entities.append((entity, 'media'))
                if entity['type'] == 'photo':
                    if 'thumb' in entity['sizes']:
                        imgs.append(entity['media_url'] + ':thumb')
                    elif 'small' in entity['sizes']:
                        imgs.append(entity['media_url'] + ':small')
                    else:
                        imgs.append(entity['media_url'])
        entities = reversed(sorted(
            entities,
            key=lambda (entity, type_): entity['indices']))
        # Removes media urls, and lengthens normal urls
        for (entity, type_) in entities:
            if type_ == 'url':
                text = (text[0:entity['indices'][0]] +
                        entity['expanded_url'] + text[entity['indices'][1]:])
            if type_ == 'media':
                text = (text[0:entity['indices'][0]] +
                        text[entity['indices'][1]:])
        return unicode(xml.unescape(text)), imgs

    def create_surface(self):
        # Helvetica is the closest to twitter's special font
        helvetica = font.SysFont('helvetica', config.getint('font', 'size'))
        surfs = []
        image = image_handler.get_image(self.json['user']['profile_image_url'])
        profile_pic = pygame.transform.scale(image, (70, 70))
        surfs.append(profile_pic)
        screen_name = self.json['user']['screen_name']
        lines = self.text.split('\n')
        name = helvetica.render('@' + screen_name, 1, BLACK)
        surfs.append(name)
        content = []
        for line in lines:
            words = [Word(word) for word in line.split()]
            word_surfs = []
            for word in words:
                try:
                    surf = helvetica.render(word.text + '  ', 1, word.color)
                    word_surfs.append(surf)
                except:
                    pass
            if word_surfs == []:
                continue
            width = sum([surf.get_width() for surf in word_surfs])
            height = max([surf.get_height() for surf in word_surfs])
            line = pygame.Surface((width, height))
            line.fill(WHITE)
            blit_list(word_surfs, line)
            content.append(line)
        popularity_count = ''
        if self.favorite_count > 0:
            popularity_count += 'Favorites: ' + str(self.favorite_count) + ' '
        if self.retweet_count > 0:
            popularity_count += 'Retweets: ' + str(self.retweet_count)
        if len(popularity_count) > 0:
            popularity_bar = helvetica.render(popularity_count, 1, BLACK)
        else:
            # Ensures that there is still space at the bottom
            # if it is retweeted later
            popularity_bar = helvetica.render('Retweets:', 1, BLACK)
            popularity_bar.fill(WHITE)
        content.append(popularity_bar)
        content.extend([image_handler.get_image(img) for img in self.imgs])
        width = max([x.get_width() for x in content])
        height = sum([x.get_height() for x in content])
        content_surf = pygame.Surface((width, height))
        content_surf.fill(WHITE)
        blit_list(content, content_surf)
        tail_length = width / 5
        width += BORDER_WIDTH + tail_length
        height += 2 * BORDER_HEIGHT
        bubble_surf = pygame.Surface((width, height))
        bubble_surf.fill(TWITTER_BLUE)
        speech_bubble = pygame.image.load('speech.png')
        bubble_surf.blit(
            pygame.transform.scale(speech_bubble, (width, height)), [0, 0])
        bubble_surf.blit(content_surf, [tail_length, BORDER_HEIGHT])
        surfs.append(bubble_surf)
        width = max([x.get_width() for x in surfs])
        height = sum([x.get_height() for x in surfs])
        tweet = pygame.Surface((width, height))
        tweet.fill(TWITTER_BLUE)
        blit_list(surfs, tweet)
        return tweet

    def update(self, json):
        self.json = json
        if (self.retweet_count != json['retweet_count'] or
                self.favorite_count != json['favorite_count']):
            self.retweet_count = json['retweet_count']
            self.favorite_count = json['favorite_count']
            tweet_surface = self.create_surface()
            pygame.image.save(
                tweet_surface,
                os.path.join("images", str(self.id) + ".png"))


class Word(object):

    def __init__(self, text):
        self.text = text
        ttext = text[0:1]
        if ttext == '#' or ttext == '@':
            self.color = BLUE
        elif len(text) > 4 and text[0:4] == 'http':
            self.color = BLUE
        else:
            self.color = BLACK


def encode_tweet(o):
    if isinstance(o, Tweet):
        x = o.__dict__
        x['class'] = 'Tweet'
    elif isinstance(o, pygame.Rect):
        x = {'left': o.left,
             'top': o.top,
             'width': o.width,
             'height': o.height,
             'class': "Rect"}
    else:
        raise TypeError("Not a Tweet!")
    return x


def decode_tweet(dictionary):
    """
    Decodes JSON into Pygame Rects and Tweet Objects (as long as they
    were encoded with TweetEncoder).
    """
    if 'class' in dictionary:
        if dictionary['class'] == 'Tweet':
            return Tweet(
                dictionary['json'],
                decode_tweet(dictionary['rect']))
        elif dictionary['class'] == 'Rect':
            return pygame.Rect(
                dictionary['left'],
                dictionary['top'],
                dictionary['width'],
                dictionary['height'])
    return dictionary
