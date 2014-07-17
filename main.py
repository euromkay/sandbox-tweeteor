import pygame, sys
from tweetsearcher import *
from tweetviewer import *
from threading import Thread, Lock
from pygame.locals import *
# Allows the user to interact with the program (view/change search parameters, exit). Currently only controllable through the terminal.
def inputHandler(searcher, exitor):
    while True:
        with exitor.lock:
            if exitor.exited:
                break#closes thread
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
            f = searcher.addUser
        elif method == '2':
            f = searcher.removeUser
        elif method == '3':
            f = searcher.addHashtag
        elif method == '4':
            f = searcher.removeHashtag
        elif method == '5':
            f = searcher.excludeWord
        elif method == '6':
            f = searcher.removeExcludedWord
        elif method == '7':
            f = searcher.excludeUser
        elif method == '8':
            f = searcher.removeExcludedUser
        elif method == '9':
            l = searcher.getUsers()
            for user in l:
                print user
            continue
        elif method == '10':
            l = searcher.getHashtags()
            for tag in l:
                print tag
            continue
        elif method == '11':
            l = searcher.getExcludedWords()
            for word in l:
                print word
            continue
        elif method == '12':
            l = searcher.getExcludedUsers()
            for user in l:
                print user
            continue
        elif method == '13':#Exits thread, and tells other threads to do the same
            with exitor.lock:
                exitor.exited = True
                break
        else:
            continue
        f(raw_input())
        
#Class for keeping track of whether the program has been closed (so that no threads are left running)        
class Exitor:
    def __init__(self):
        self.exited = False
        self.lock = Lock()
pygame.init()
searcher = TweetSearcher()
searcher.start()
view = TweetViewer(searcher, (1800, 600))
view.start()
exitor = Exitor()
inHandler = Thread(target = inputHandler, args = (searcher, exitor))
inHandler.daemon = True#Makes it a daemon thread, so I don't have to manually close the thread(not working for some reason)
inHandler.start()
while True:#This loop makes sure the program closes when it needs to, and so that it doesn't freeze up(not responding)
    with exitor.lock:
        if exitor.exited:
            pygame.quit()
            sys.exit()
    for event in pygame.event.get():
        if event.type == QUIT:
            with exitor.lock:
                exitor.exited = True
    pygame.time.wait(10)#Without this, uses too much cpu time
