import pygame, sys
from controller import *
from searcher import *
from viewer import *
from threading import Thread, Lock
from pygame.locals import *
from socket import *

class Server(Thread):
	def __init__(self, address, viewer):
		Thread.__init__(self)
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.viewer = viewer
		self.daemon = True
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.viewer.addClient(client)
		
pygame.init()
exitor = Exitor()
searcher = Searcher()
searcher.start()
view = Viewer(searcher, exitor) #info.current_w and info.current_h are the width and height of the entire screen
view.start()
address = ('', int(raw_input("Enter port #")))
server = Server(address, view)
server.start()
inHandler = Controller(searcher, exitor)
inHandler.start()
while True:#This loop makes sure the program closes when it needs to, and so that it doesn't freeze up(not responding)
    with exitor.lock:
        if exitor.exited:
            pygame.quit()
            sys.exit()
    pygame.time.wait(10)#Without this, uses too much cpu time
