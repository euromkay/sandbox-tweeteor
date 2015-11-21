"""
Interacts with Twitter and sends data to the clients
(using the Server module as an intermediary).
"""
import time
import json
import logging
from base64 import b64encode
from collections import OrderedDict
from threading import Thread, Lock, Event

import requests
import pygame

from tweet import Tweet, encode_tweet
from server import Server
from rectangle_handler import position_rectangles, random_position
from constants import SCR_SIZE
import safesearch

import config2


class Searcher(Thread):
    """
    A dedicated thread for searching twitter and processing tweets.
    The Searcher object maintains several lists of search terms,
    which can be accessed by their corresponding methods.
    """

    def __init__(self, key, secret, address):
        
        """
        Connect to Twitter using the given API key and API secret,
        and open a socket at the given address for Tweeteor clients
        to connect to.
        """
        Thread.__init__(self, name='Searcher')
        # Twitter requires credentials to be Base64 encoded.
        credentials = b64encode(key + ':' + secret)
        headers = {'Authorization': 'Basic ' + credentials,
                   'Content-Type':
                       'application/x-www-form-urlencoded;charset=UTF-8'}
        r = requests.post(
            'https://api.twitter.com/oauth2/token',
            headers=headers,
            data='grant_type=client_credentials')
        token = r.json()['access_token']
        self.headers = {'Authorization': 'Bearer ' + token}
        self.users = []
        self.hashtags = []
        self.excluded_words = []
        self.excluded_users = []
        self.lock = Lock()
        self.is_search_updated = True
        self.server = Server(address)
        self.exit = Event()
        # We use an OrderedDict because it allows us to order the tweets
        # (same order they appear on screen), while still being able
        # to quickly access Tweet's by ID.
        self.tweets = OrderedDict()

    def add_user(self, user):
        """Follow the given user."""
        with self.lock:
            if user not in self.users:
                self.users.append(user)
        self.is_search_updated = True

    def add_hashtag(self, tag):
        """Follow the given hashtag"""
        with self.lock:
            if tag not in self.hashtags:
                self.hashtags.append(tag)
        self.is_search_updated = True

    def remove_user(self, user):
        """
        Remove the given user from the follow list
        (do nothing if the user is not currently being followed).
        """
        with self.lock:
            if user in self.users:
                self.users.remove(user)
        self.is_search_updated = True

    def remove_hashtag(self, tag):
        """
        Remove the given hashtag from the follow list
        (do nothing if the hashtag is not currently being followed).
        """
        with self.lock:
            if tag in self.hashtags:
                self.hashtags.remove(tag)
        self.is_search_updated = True

    def exclude_word(self, word):
        """Block tweets containing the given word."""
        with self.lock:
            if word not in self.excluded_words:
                self.excluded_words.append(word)
        self.is_search_updated = True

    def remove_excluded_word(self, word):
        """Stop blocking the given word."""
        with self.lock:
            if word in self.excluded_words:
                self.excluded_words.remove(word)
        self.is_search_updated = True

    def exclude_user(self, user):
        """Block tweets from the given user."""
        with self.lock:
            if user not in self.excluded_users:
                self.excluded_users.append(user)
        self.is_search_updated = True

    def remove_excluded_user(self, user):
        """Stop blocking the given user."""
        with self.lock:
            if user in self.excluded_users:
                self.excluded_users.remove(user)
        self.is_search_updated = True

    def run(self):
        """
        Search Twitter, process the results, and
        send data to the clients, over and over. Shut down
        Tweeteor when it is told to exit (e.g. by the Controller).
        """
        screen = pygame.Surface(SCR_SIZE)
        self.server.start()
        tweet_positions = dict()
        try:
            while not self.exit.is_set():
                if self.is_search_updated:
                    # This ensures that all tweets match the current search,
                    # and are not just leftovers from a previous one.
                    self.tweets.clear()
                    self.is_search_updated = False
                search = self.get_search()
                # Twitter returns an error for empty searches,
                # so this is a way around it
                if search != '':
                    # Check twitter API for all parameters
                    params = {'q': search,
                              'result_type': 'recent',
                              'lang': 'en',
                              'count': 100}
                    r = requests.get(
                        'https://api.twitter.com/1.1/search/tweets.json',
                        headers=self.headers,
                        params=params)
                    if 'statuses' in r.json():
                        tweets = [tweet for tweet in safesearch.safe_filter(r.json()['statuses']) if 'retweeted_status' not in tweet]
                    else:
                        print r.json()
                        continue
                    for tweet in tweets:
                        if tweet['id'] in self.tweets:
                            self.tweets[tweet['id']].update(tweet)
                        else:
                            self.tweets[tweet['id']] = Tweet(tweet)
                #if len(self.tweets) > 0:
                    # Rotating the tweets, to simulate scrolling.
                    #tweet = self.tweets.popitem(False)[1]
                    #self.tweets[tweet.id] = tweet
                tweets = list(self.tweets.values())
                if config2.config['random_position']:
                    random_position(tweets, screen, tweet_positions)
                else:
                    position_rectangles(tweets, screen)
                msg = json.dumps(tweets, default=encode_tweet)
                self.server.send(msg)
                # Don't want the loop to run to often,
                # or else you hit the twitter rate limit
                time.sleep(2)
        except:
            # This block does not actually handle the error, only log it.
            # That's why we re-raise the error, so that important errors
            # are not silenced.
            logging.exception("Fatal Exception Thrown")
            raise
        # A finally block guarantees that Tweeteor will shut down properly,
        # even if a fatal exception is thrown.
        finally:
            self.server.send('exit')

    def get_search(self):
        """
        Take the data from the search term lists and format it
        so that Twitter can understand it. Return the formatted
        info as a string.
        """
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
