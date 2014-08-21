from threading import Thread, Lock
import threading, sys, pygame, logging

# Allows the user to interact with the program (view/change search parameters, exit). Currently only controllable through the terminal.
class Controller(Thread):
	def __init__(self, searcher):
		Thread.__init__(self, name = 'Controller')
		self.searcher = searcher
	def run(self):
	    while True:
		logging.debug("running")
		print '''              1 - Add User
		      2 - Remove User
		      3 - Add Hashtag
		      4 - Remove Hashtag
		      5 - Exclude Word
		      6 - Remove Excluded Word
		      7 - Exclude User
		      8 - Remove Excluded User
		      9 - List Users
		      10 - List Hashtags
		      11 - List Excluded Words
		      12 - List Excluded Users
		      13 - Exit'''
		method = raw_input()
		if method == '1':
		    f = self.searcher.addUser
		elif method == '2':
		    f = self.searcher.removeUser
		elif method == '3':
		    f = self.searcher.addHashtag
		elif method == '4':
		    f = self.searcher.removeHashtag
		elif method == '5':
		    f = self.searcher.excludeWord
		elif method == '6':
		    f = self.searcher.removeExcludedWord
		elif method == '7':
		    f = self.searcher.excludeUser
		elif method == '8':
		    f = self.searcher.removeExcludedUser
		elif method == '9':
		    l = self.searcher.getUsers()
		    for user in l:
			print user
		    continue
		elif method == '10':
		    l = self.searcher.getHashtags()
		    for tag in l:
			print tag
		    continue
		elif method == '11':
		    l = self.searcher.getExcludedWords()
		    for word in l:
			print word
		    continue
		elif method == '12':
		    l = self.searcher.getExcludedUsers()
		    for user in l:
			print user
		    continue
		elif method == '13': #Closes all nondaemon threads, then quits pygame
			self.searcher.exit.set()
			self.searcher.join()
			pygame.quit()
			sys.exit()
		else:
		    continue
		f(raw_input())
