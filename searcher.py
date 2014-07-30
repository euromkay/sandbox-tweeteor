from base64 import b64encode
from threading import Thread, Lock, Event
from tempfile import NamedTemporaryFile
import requests, time, sys, json, logging
#Searches twitter based on user-set parameters, and makes a list of the tweets(dictionaries)
class Searcher(Thread):
	def __init__(self, credentials, server):
                Thread.__init__(self, name = 'Searcher')
                #Authentication
                headers = {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
                r = requests.post('https://api.twitter.com/oauth2/token', headers = headers, data = 'grant_type=client_credentials')
                bearerToken = r.json()['access_token']
		self._headers = {'Authorization': 'Bearer ' + bearerToken}
		#End of Authentication
		self._userList = []
		self._hashtagList = []
		self._excludedWordList = []
		self._excludedUserList = []
		self._searchLock = Lock()
		self.server = server
		self.exit = Event()
		self.tempfiles = {}
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
			if self.exit.isSet():
				self.server.send('exit')
				return
                        search = self._getSearch()
                        if search == '':#Twitter returns an error for empty searches, so this is a way around it
                                tweets = []
                        else:
                                params = {'q': self._getSearch(), 'result_type': 'recent', 'lang': 'en', 'count': 100}#Check twitter API for all parameters
                                r = requests.get('https://api.twitter.com/1.1/search/tweets.json', headers = self._headers, params = params)
                                tweets = [ tweet for tweet in r.json()['statuses'] if 'retweeted_status' not in tweet]#No need for boring retweets
			mediaObjs = []
			for tweet in tweets:
				if 'media' in tweet['entities']:
					mediaObjs.extend([entity for entity in tweet['entities']['media'] if entity['type'] == 'photo'])
			logging.debug('starting tempfile use')
			for mediaObj in mediaObjs:
				if mediaObj['media_url'] in self.tempfiles:
					self.tempfiles[mediaObj['media_url']].inUse = True
					logging.debug(mediaObj['media_url'] + ' already saved')
					continue
				if 'thumb' in mediaObj['sizes']:
					imgRequest = requests.get(mediaObj['media_url'] + ':thumb')
					logging.debug(mediaObj['media_url'] + ' dowloaded')
				elif 'small' in mediaObj['sizes']:
					imgRequest = requests.get(mediaObj['media_url'] + ':small')
					logging.debug(mediaObj['media_url'] + ' dowloaded')
				else:
					imgRequest = requests.get(mediaObj['media_url'])
					logging.debug(mediaObj['media_url'] + ' dowloaded')
				if imgRequest.status_code == 200:#make sure the link worked
					temp = NamedTemporaryFile(prefix = mediaObj['media_url'].replace('/', ''))
					temp.write(imgRequest.content)#Saves image in temp file so it only has to be downloaded once
					temp.seek(0)#moves to start of file
					temp.inUse = True
					self.tempfiles[mediaObj['media_url']] = temp 
					logging.debug(mediaObj['media_url'] + ' saved')
			imgs = {}
			for key in self.tempfiles:
				f = self.tempfiles[key]
				f.seek(0)
				imgs[key] = b64encode(f.read())
			msg = json.dumps((tweets, imgs))
			self.server.send(msg)
			self.deleteUnusedTempfiles()
			logging.debug('done with tempfiles')
			time.sleep(2)#Don't want the loop to run to often, or else you hit the twitter rate limit
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
	#Helper method to clear out images that aren't needed
	def deleteUnusedTempfiles(self):
		deletedKeys = []
		tempList = iter(self.tempfiles)
		for key in tempList:
			if not self.tempfiles[key].inUse:
				self.tempfiles[key].close()#Tempfiles are deleted when closed
				deletedKeys.append(key)
				logging.debug('deleting ' + key)
			self.tempfiles[key].inUse = False
		for key in deletedKeys:
			del self.tempfiles[key]#Removing file from list
