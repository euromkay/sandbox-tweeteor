"""Classes and functions for working with tweets."""
import os
import logging
import xml.sax.saxutils as xml
from ConfigParser import SafeConfigParser

import pygame

import image_handler
from rectangle_handler import make_row, make_column

config = SafeConfigParser()
config.read('config')
pygame.font.init()

BORDER_WIDTH = 20
BORDER_HEIGHT = 20
WHITE = pygame.Color(255, 255, 255, 255)
BLACK = pygame.Color(0, 0, 0, 255)
BLUE = pygame.Color(0, 0, 255, 255)
TWITTER_BLUE = pygame.Color(154, 194, 223)


class Tweet(object):
    """
    A representation of a tweet.
    """
    # Helvetica is the closest to twitter's special font
    font = pygame.font.SysFont('helvetica', config.getint('font', 'size'))
    cache_dir = os.path.join("cache", "tweets")

    def __init__(self, json):
        """
        Creates a tweet object by parsing json. This json is in
        the format produced by the Twitter API, not the format created by
        encode_tweet.
        """
        self.id = json['id']
        self.retweet_count = json['retweet_count']
        self.favorite_count = json['favorite_count']
        self.profile_image_url = json['user']['profile_image_url']
        self.screen_name = json['user']['screen_name']
        text, self.imgs = Tweet.expand_links(json)
        lines = text.split('\n')
        self.lines = []
        for line in lines:
            self.lines.append([Word(word) for word in line.split()])
        surface = self.create_surface()
        self.save_surface(surface)
        self.rect = surface.get_rect()

    def get_rect(self):
        """Returns a Rect representing the location and size of the tweet."""
        return self.rect

    def get_surface(self):
        """
        Returns a Surface depicting the Tweet
        """
        filename = os.path.join(Tweet.cache_dir, str(self.id) + ".png")
        return pygame.image.load(filename)

    def update(self, json):
        """
        Updates the Tweet based on a newer version of the JSON.
        (e.g. updates retweet and favorite counts).
        """
        if (self.retweet_count != json['retweet_count'] or
                self.favorite_count != json['favorite_count']):
            self.retweet_count = json['retweet_count']
            self.favorite_count = json['favorite_count']
            tweet_surface = self.create_surface()
            self.save_surface(tweet_surface)

    def create_surface(self):
        """Creates a Surface depicting the Tweet."""
        #TODO: Needs refactoring (including the helper methods).
        surfs = []
        image = image_handler.get_image(self.profile_image_url)
        profile_pic = pygame.transform.scale(image, (70, 70))
        surfs.append(profile_pic)
        name = Tweet.font.render('@' + self.screen_name, 1, BLACK)
        surfs.append(name)
        text = Tweet.create_body(self.lines)
        content = [text]
        content.extend([image_handler.get_image(img) for img in self.imgs])
        popularity_bar = self.create_popularity_surface()
        content.append(popularity_bar)
        content_surf = make_column(content, WHITE)
        surfs.append(Tweet.create_bubble(content_surf))
        tweet = make_column(surfs, TWITTER_BLUE)
        return tweet

    def save_surface(self, surface):
        """
        Saves a copy of the surface to a cache, to avoid
        unnecessary regeneration of the Tweet Surface.
        """
        pygame.image.save(
            surface,
            os.path.join(Tweet.cache_dir, str(self.id) + ".png"))

    @staticmethod
    def expand_links(json):
        """
        Parses through the Twitter API JSON for a tweet, and returns
        a modified version of the text (e.g. expanding URLs), and a list
        of urls for images found in the tweet. Return value is in the
        format (text, images).
        """
        text = json['text']
        imgs = []
        entities = []  # List of all urls and media urls in tweet
        if 'urls' in json['entities']:  # adds urls to entities
            entities.extend(
                [(entity, 'url') for entity in json['entities']['urls']])
        if 'media' in json['entities']:  # adds mediau urls to entities
            for entity in json['entities']['media']:
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

    @staticmethod
    def create_bubble(content):
        """
        Takes a surface (content) and wraps it in a speech bubble,
        which is returned to the caller.
        """
        width = content.get_width()
        tail_length = width / 5
        width += BORDER_WIDTH + tail_length
        height = content.get_height() + 2 * BORDER_HEIGHT
        destination = pygame.Surface((width, height))
        destination.fill(TWITTER_BLUE)
        speech_bubble = pygame.image.load('speech.png')
        destination.blit(
            pygame.transform.scale(speech_bubble, (width, height)), [0, 0])
        destination.blit(content, [tail_length, BORDER_HEIGHT])
        return destination

    @staticmethod
    def create_body(lines):
        """
        Create a surface representing the body of a tweet
        (the actual words in the tweet). Takes a matrix of Words
        (each row is a line) as input.
        """
        surfs = []
        for line in lines:
            word_surfs = []
            for word in line:
                try:
                    surf = Tweet.font.render(word.text + '  ', 1, word.color)
                    word_surfs.append(surf)
                except:
                    logging.exception("Error when rendering Word")
            if len(word_surfs) == 0:
                continue
            line = make_row(word_surfs, WHITE)
            surfs.append(line)
        return make_column(surfs, WHITE)

    def create_popularity_surface(self):
        """
        Creates a surface holding a favorite count and a retweet count
        for the Tweet.
        """
        popularity_count = ''
        if self.favorite_count > 0:
            popularity_count += 'Favorites: ' + str(self.favorite_count) + ' '
        if self.retweet_count > 0:
            popularity_count += 'Retweets: ' + str(self.retweet_count)
        if len(popularity_count) > 0:
            popularity_bar = Tweet.font.render(popularity_count, 1, BLACK)
        else:
            # Ensures that there is still space at the bottom
            # if it is retweeted later
            popularity_bar = Tweet.font.render('Retweets:', 1, BLACK)
            popularity_bar.fill(WHITE)
        return popularity_bar


class Word(object):
    """
    A representation of a word in the tweet body
    and its attributes (currently only color).
    """

    def __init__(self, text):
        """
        Sets the word as Blue if it is a link,
        hashtag, or username, and as black otherwise.
        """
        self.text = text
        ttext = text[0:1]
        if ttext == '#' or ttext == '@':
            self.color = BLUE
        elif len(text) > 4 and text[0:4] == 'http':
            self.color = BLUE
        else:
            self.color = BLACK


def encode_tweet(o):
    """
    Encodes Tweet objects as JSON. Also encodes other objects
    needed as attributes (Rects, Words, and Colors).
    Does NOT encode tweets in the same way the Twitter API does.
    """
    if isinstance(o, Tweet):
        x = o.__dict__
        x['class'] = 'Tweet'
    elif isinstance(o, pygame.Rect):
        x = {'left': o.left,
             'top': o.top,
             'width': o.width,
             'height': o.height,
             'class': "Rect"}
    elif isinstance(o, Word):
        x = o.__dict__
        x['class'] = 'Word'
    elif isinstance(o, pygame.Color):
        x = {'r': o.r, 'g': o.g, 'b': o.b, 'a': o.a}
        x['class'] = 'Color'
    else:
        raise TypeError("Not a Tweet!")
    return x


def decode_tweet(dictionary):
    """
    Decode Tweets from json. Also decodes Words, Colors, and Rects,
    as they are attributes of Tweets.
    Does NOT decode tweets from Twitter API; only decodes Tweets
    encoded by encode_tweet.
    """
    if 'class' in dictionary:
        if dictionary['class'] == 'Tweet':
            # Allows us to bypass normal initialization,
            # avoiding unnecessary work (e.g. surface generation).
            tweet = object.__new__(Tweet)
            tweet.__dict__ = dictionary
            return tweet
        elif dictionary['class'] == 'Word':
            word = object.__new__(Word)
            word.__dict__ = dictionary
            return word
        elif dictionary['class'] == 'Color':
            color = pygame.Color(
                dictionary['r'],
                dictionary['g'],
                dictionary['b'],
                dictionary['a'])
            return color
        elif dictionary['class'] == 'Rect':
            return pygame.Rect(
                dictionary['left'],
                dictionary['top'],
                dictionary['width'],
                dictionary['height'])
    return dictionary
