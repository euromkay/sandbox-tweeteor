import base64, requests, time, threading, auth

class TweetSearcher(threading.Thread):
	def __init__(self):
                threading.Thread.__init__(self)
                credentials = base64.b64encode(auth.key + ':' + auth.secret)
                headers = {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
                r = requests.post('https://api.twitter.com/oauth2/token', headers = headers, data = 'grant_type=client_credentials')
                bearerToken = r.json()['access_token']
		self._headers = {'Authorization': 'Bearer ' + bearerToken}
		self.daemon = True
		self.recentList = []
		self.listLock = threading.Condition()
		self._userList = []
		self._hashtagList = []
		self._excludedWordList = []
		self._excludedUserList = []
		self._searchLock = threading.Lock()
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
                        if search == '':
                                tweets = []
                        else:
                                params = {'q': self._getSearch(), 'result_type': 'recent', 'lang': 'en', 'count': 50}
                                r = requests.get('https://api.twitter.com/1.1/search/tweets.json', headers = self._headers, params = params)
                                tweets = [ tweet for tweet in r.json()['statuses'] if 'retweeted_status' not in tweet]
			with self.listLock:
				self.recentList = tweets
			time.sleep(4)
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
