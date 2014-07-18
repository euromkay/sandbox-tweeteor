import pygame, sys
from controller import *
from tweetsearcher import *
from tweetviewer import *
from threading import Thread, Lock
from pygame.locals import *

pygame.init()
exitor = Exitor()
searcher = TweetSearcher()
searcher.start()
view = TweetViewer(searcher, (1800, 600), exitor)
view.start()
inHandler = Controller(searcher, exitor)
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
