import requests, time, auth, sys
from base64 import b64encode
from threading import Thread, Lock, Condition
#Searches twitter based on user-set parameters, and makes a list of the tweets(dictionaries)
class Searcher(Thread):
	def __init__(self):
                Thread.__init__(self, name = 'Searcher')
                #Authentication
                credentials = b64encode(auth.key + ':' + auth.secret)
                headers = {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
                r = requests.post('https://api.twitter.com/oauth2/token', headers = headers, data = 'grant_type=client_credentials')
                bearerToken = r.json()['access_token']
		self._headers = {'Authorization': 'Bearer ' + bearerToken}
		#End of Authentication
		self.recentList = []
		self.listLock = Condition()#I used a condition instead of a lock here, so tweetviewer only updates when needed
		self._userList = []
		self._hashtagList = []
		self._excludedWordList = []
		self._excludedUserList = []
		self._searchLock = Lock()
		self.setDaemon(True)
	def getUsers(self):
                with self._searchLock:
                        return list(self._userList)
        def getHashtags(self):
                with self._searchLock:
                        return list(self._hashtagList)
        def getExcludedWords(self):
                with self._searchLock:
                        return list(self._excludedWordList)
        def getExcludedUsers(self):
                with self._searchLock:
                        return list(self._excludedUserList)
	def addUser(self, user):
		with self._searchLock:
                        if user not in self._userList:
                                self._userList.append(user)
	def addHashtag(self, tag):
		with self._searchLock:
                        if tag not in self._hashtagList:
                                self._hashtagList.append(tag)
	def removeUser(self, user):
		with self._searchLock:
                        if user in self._userList:
                                self._userList.remove(user)
	def removeHashtag(self, tag):
		with self._searchLock:
                        if tag in self._hashtagList:
                                self._hashtagList.remove(tag)
	def excludeWord(self, word):
		with self._searchLock:
                        if word not in self._excludedWordList:
                                self._excludedWordList.append(word)
	def removeExcludedWord(self, word):
		with self._searchLock:
                        if word in self._excludedWordList:
                                self._excludedWordList.remove(word)
        def excludeUser(self, user):
		with self._searchLock:
                        if user not in self._excludedUserList:
                                self._excludedUserList.append(user)
	def removeExcludedUser(self, user):
		with self._searchLock:
                        if user in self._excludedUserList:
                                self._excludedUserList.remove(user)
	def run(self):
                while True:
                        search = self._getSearch()
                        if search == '':#Twitter returns an error for empty searches, so this is a way around it
                                tweets = []
                        else:
                                params = {'q': self._getSearch(), 'result_type': 'recent', 'lang': 'en', 'count': 100}#Check twitter API for all parameters
                                r = requests.get('https://api.twitter.com/1.1/search/tweets.json', headers = self._headers, params = params)
                                tweets = [ tweet for tweet in r.json()['statuses'] if 'retweeted_status' not in tweet]#No need for boring retweets
			with self.listLock:
				self.recentList = tweets
				self.listLock.notify()#Tells tweetviewer to update its screen
			time.sleep(4)#Don't want the loop to run to often, or else you hit the twitter rate limit
	#Helper method for assembling search query
	def _getSearch(self):
                search = ''
		with self._searchLock:
                        for user in self._userList:
                                search += 'from:' + user + ' OR ' 
			for hashtag in self._hashtagList:
                                search += '#' + hashtag + ' OR '
			search = search[0:len(search) - 4]
			for exuser in self._excludedUserList:
                                search += ' -from:' + exuser
			for word in self._excludedWordList:
                                search += ' -' + word
                return search
