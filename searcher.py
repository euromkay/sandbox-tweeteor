from server import *
from tweet import *
from threading import Thread, Lock, Event
from rectangleHandler import *
import requests, time, sys, json, logging
from collections import *

encoder = RectangleEncoder()
config = SafeConfigParser()
config.read('server.conf')
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = config.getint('window', 'width'), config.getint('window', 'height')
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_SIZE = SCR_WIDTH, SCR_HEIGHT = WIN_WIDTH * WIN_PER_ROW, WIN_HEIGHT * WIN_PER_COLUMN
#Searches twitter based on user-set parameters, and makes a list of the tweets(dictionaries)
class Searcher(Thread):
        def __init__(self, credentials, address):
            Thread.__init__(self, name = 'Searcher')
            #Authentication
            headers = {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
            r = requests.post('https://api.twitter.com/oauth2/token', headers = headers, data = 'grant_type=client_credentials')
            bearerToken = r.json()['access_token']
            self.headers = {'Authorization': 'Bearer ' + bearerToken}
            #End of Authentication
            self.userList = []
            self.hashtagList = []
            self.excludedWordList = []
            self.excludedUserList = []
            self.searchLock = Lock()
            self.server = Server(address, self)
            self.screen = pygame.Surface(SCR_SIZE)
            self.exit = Event()
            self.tweets = OrderedDict()
            self.tweetLock = Lock()
        def getUsers(self):
                with self.searchLock:
                        return list(self.userList)
        def getHashtags(self):
                with self.searchLock:
                        return list(self.hashtagList)
        def getExcludedWords(self):
                with self.searchLock:
                        return list(self.excludedWordList)
        def getExcludedUsers(self):
                with self.searchLock:
                        return list(self.excludedUserList)
        def addUser(self, user):
                with self.searchLock:
                        if user not in self.userList:
                                self.userList.append(user)
        def addHashtag(self, tag):
                with self.searchLock:
                        if tag not in self.hashtagList:
                                self.hashtagList.append(tag)
        def removeUser(self, user):
                with self.searchLock:
                        if user in self.userList:
                                self.userList.remove(user)
        def removeHashtag(self, tag):
                with self.searchLock:
                        if tag in self.hashtagList:
                                self.hashtagList.remove(tag)
        def excludeWord(self, word):
                with self.searchLock:
                        if word not in self.excludedWordList:
                                self.excludedWordList.append(word)
        def removeExcludedWord(self, word):
                with self.searchLock:
                        if word in self.excludedWordList:
                                 self.excludedWordList.remove(word)
        def excludeUser(self, user):
                with self.searchLock:
                        if user not in self.excludedUserList:
                                self.excludedUserList.append(user)
        def removeExcludedUser(self, user):
        	with self.searchLock:
                        if user in self.excludedUserList:
                                self.excludedUserList.remove(user)
        def run(self):
                self.server.start()
                while True:
                        logging.debug("running")
                        if self.exit.isSet():
                                self.server.send('exit')
                                return
                        search = self.getSearch()
                        if search == '':#Twitter returns an error for empty searches, so this is a way around it
                                tweets = []
                        else:
                            params = {'q': self.getSearch(), 'result_type': 'recent', 'lang': 'en', 'count': 100}#Check twitter API for all parameters
                            r = requests.get('https://api.twitter.com/1.1/search/tweets.json', headers = self.headers, params = params)
                            tweets = [Tweet(tweet) for tweet in r.json()['statuses'] if 'retweeted_status' not in tweet]#No need for boring retweets
                            with self.tweetLock:
                                for tweet in tweets:
                                    self.tweets[tweet.id] = tweet
                        with self.tweetLock:
                            if len(self.tweets) > 0:
                                tweet = self.tweets.popitem(False)[1]
                                self.tweets[tweet.id] = tweet
                                tweets = list(self.tweets.values())
                                positionRectangles(self.screen, tweets)
                        msg = encoder.encode(tweets)
                        self.server.send(msg)
                        time.sleep(2)#Don't want the loop to run to often, or else you hit the twitter rate limit
        #Helper method for assembling search query
        def getSearch(self):
                search = ''
                with self.searchLock:
                        for user in self.userList:
                                search += 'from:' + user + ' OR ' 
                        for hashtag in self.hashtagList:
                                search += '#' + hashtag + ' OR '
                        search = search[0:len(search) - 4]
                        for exuser in self.excludedUserList:
                                search += ' -from:' + exuser
                        for word in self.excludedWordList:
                                search += ' -' + word
                return search
        def getWelcomeData(self):
                with self.tweetLock:
                        tweets = list(self.tweets.values())
                return encoder.encode(tweets)
