import pygame, sys, logging
from controller import *
from searcher import *
from viewer import *
from threading import Thread, Lock, Event
from pygame.locals import *
from socket import *

class Server(Thread):
	def __init__(self, address, viewer):
		Thread.__init__(self, name = 'Server')
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.viewer = viewer
		self.setDaemon(True)
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.viewer.addClient(client)
		

logging.basicConfig(filename = 'tweeteor.log', level=logging.DEBUG, format='[%(levelname)s] (%(threadName)s) %(message)s')

pygame.init()
searcher = Searcher()
searcher.start()
view = Viewer(searcher)
view.start()
address = ('', int(raw_input("Enter port #")))
server = Server(address, view)
server.start()
inHandler = Controller(searcher)
inHandler.start()
