from server import *
from tweet import *
from base64 import b64encode
from threading import Thread, Lock, Event
from tempfile import NamedTemporaryFile
from rectangleHandler import *
import requests, time, sys, json, logging

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
            self.tweets = []
            self.tweetLock = Lock()
            self.tempfiles = {}
            self.tempfileLock = Lock()
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
                lastID = 1
                while True:
                        logging.debug("running")
                        if self.exit.isSet():
                                self.server.send('exit')
                                with self.tempfileLock:
                                        for key in self.tempfiles:
                                                self.tempfiles[key].close()
                                return
                        search = self.getSearch()
                        if search == '':#Twitter returns an error for empty searches, so this is a way around it
                                tweets = []
                        else:
                            params = {'q': self.getSearch(), 'result_type': 'recent', 'lang': 'en', 'count': 100, 'since_id': lastID}#Check twitter API for all parameters
                            r = requests.get('https://api.twitter.com/1.1/search/tweets.json', headers = self.headers, params = params)
                            #try:
                            tweets = [Tweet(tweet) for tweet in r.json()['statuses'] if 'retweeted_status' not in tweet]#No need for boring retweets
                            #except:
                            #        logging.debug(r.text)
                        mediaObjs = []
                        imgs = {}
                        with self.tweetLock:
                                tweets.extend(self.tweets)
                                self.tweets = [tweet for (tweet, rectangle) in positionRectangles(self.screen, tweets)]
                                if len(self.tweets) > 0:
                                    lastID = self.tweets[0].id
                                for tweet in self.tweets:
                                    mediaObjs.extend(tweet.imgs)
                        with self.tempfileLock:
                                for mediaObj in mediaObjs:
                                        key = mediaObj['media_url']
                                        if key in self.tempfiles:
                                                self.tempfiles[key].inUse = True
                                                continue
                                        if 'thumb' in mediaObj['sizes']:
                                                imgRequest = requests.get(key + ':thumb')
                                        elif 'small' in mediaObj['sizes']:
                                                imgRequest = requests.get(key + ':small')
                                        else:
                                                imgRequest = requests.get(key)
                                        if imgRequest.status_code == 200:#make sure the link worked
                                                temp = NamedTemporaryFile(prefix = key.replace('/', ''))
                                                temp.write(imgRequest.content)#Saves image in temp file so it only has to be downloaded once
                                                temp.seek(0)#moves to start of file
                                                imgs[key] = b64encode(temp.read())
                                                temp.inUse = True
                                                self.tempfiles[key] = temp 
                        with self.tweetLock:
                            msg = encoder.encode((self.tweets, imgs))
                        self.server.send(msg)
                        self.deleteUnusedTempfiles()
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
	#Helper method to clear out images that aren't needed
        def deleteUnusedTempfiles(self):
                deletedKeys = []
                with self.tempfileLock:
                        tempList = iter(self.tempfiles)
                        for key in tempList:
                                if not self.tempfiles[key].inUse:
                                        self.tempfiles[key].close()#Tempfiles are deleted when closed
                                        deletedKeys.append(key)
                                self.tempfiles[key].inUse = False
                        for key in deletedKeys:
                                self.tempfiles[key].close()
                                del self.tempfiles[key]#Removing file from list
        def getWelcomeData(self):
                with self.tweetLock:
                        tweets = self.tweets
                with self.tempfileLock:
                        imgs = {}
                        for key in self.tempfiles:
                                f = self.tempfiles[key]
                                f.seek(0)
                                imgs[key] = b64encode(f.read())
                return encoder.encode((tweets, imgs))
