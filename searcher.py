import time
import json
from collections import OrderedDict
from threading import Thread, Lock, Event

import requests
import pygame

from tweet import Tweet, encode_tweet
from server import Server
from rectangle_handler import position_rectangles
from constants import SCR_SIZE


class Searcher(Thread):

    def __init__(self, credentials, address):
        Thread.__init__(self, name='Searcher')
        # Authentication
        headers = {'Authorization': 'Basic ' + credentials,
                   'Content-Type':
                       'application/x-www-form-urlencoded;charset=UTF-8'}
        r = requests.post(
            'https://api.twitter.com/oauth2/token',
            headers=headers,
            data='grant_type=client_credentials')
        token = r.json()['access_token']
        self.headers = {'Authorization': 'Bearer ' + token}
        # End of Authentication
        self.users = []
        self.hashtags = []
        self.excluded_words = []
        self.excluded_users = []
        self.lock = Lock()
        self.is_search_updated = False
        self.server = Server(address)
        self.exit = Event()
        self.tweets = OrderedDict()

    def add_user(self, user):
        with self.lock:
            if user not in self.users:
                self.users.append(user)
        self.is_search_updated = True

    def add_hashtag(self, tag):
        with self.lock:
            if tag not in self.hashtags:
                self.hashtags.append(tag)
        self.is_search_updated = True

    def remove_user(self, user):
        with self.lock:
            if user in self.users:
                self.users.remove(user)
        self.is_search_updated = True

    def remove_hashtag(self, tag):
        with self.lock:
            if tag in self.hashtags:
                self.hashtags.remove(tag)
        self.is_search_updated = True

    def exclude_word(self, word):
        with self.lock:
            if word not in self.excluded_words:
                self.excluded_words.append(word)
        self.is_search_updated = True

    def remove_excluded_word(self, word):
        with self.lock:
            if word in self.excluded_words:
                self.excluded_words.remove(word)
        self.is_search_updated = True

    def exclude_user(self, user):
        with self.lock:
            if user not in self.excluded_users:
                self.excluded_users.append(user)
        self.is_search_updated = True

    def remove_excluded_user(self, user):
        with self.lock:
            if user in self.excluded_users:
                self.excluded_users.remove(user)
        self.is_search_updated = True

    def run(self):
        screen = pygame.Surface(SCR_SIZE)
        self.server.start()
        try:
            while not self.exit.is_set():
                if self.is_search_updated:
                    self.tweets = OrderedDict()
                    self.is_search_updated = False
                search = self.get_search()
                # Twitter returns an error for empty searches,
                # so this is a way around it
                if search == '':
                    tweets = []
                else:
                    # Check twitter API for all parameters
                    params = {'q': search,
                              'result_type': 'recent',
                              'lang': 'en',
                              'count': 100}
                    r = requests.get(
                        'https://api.twitter.com/1.1/search/tweets.json',
                        headers=self.headers,
                        params=params)
                    tweets = [tweet for tweet in r.json()['statuses']
                              # No need for boring retweets
                              if 'retweeted_status' not in tweet]
                    for tweet in tweets:
                        if tweet['id'] in self.tweets:
                            self.tweets[tweet['id']].update(tweet)
                        else:
                            self.tweets[tweet['id']] = Tweet(tweet)
                if len(self.tweets) > 0:
                    tweet = self.tweets.popitem(False)[1]
                    self.tweets[tweet.id] = tweet
                    tweets = list(self.tweets.values())
                    position_rectangles(tweets, screen)
                msg = json.dumps(tweets, default=encode_tweet)
                self.server.send(msg)
                # Don't want the loop to run to often,
                # or else you hit the twitter rate limit
                time.sleep(2)
        finally:
            self.server.send('exit')

    def get_search(self):
        search = ''
        with self.lock:
            for user in self.users:
                search += 'from:' + user + ' OR '
            for hashtag in self.hashtags:
                search += '#' + hashtag + ' OR '
            search = search[0:len(search) - 4]
            for exuser in self.excluded_users:
                search += ' -from:' + exuser
            for word in self.excluded_words:
                search += ' -' + word
            return search
