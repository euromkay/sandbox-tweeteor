import pygame, sys, logging
from base64 import b64encode
from controller import *
from searcher import *
from viewer import *
from threading import Thread, Lock, Event
from pygame.locals import *
from socket import *
from ConfigParser import SafeConfigParser

class Server(Thread):
	def __init__(self, address, viewer):
		Thread.__init__(self, name = 'Server')
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.viewer = viewer
		self.setDaemon(True) #Server automatically shutsdown when all nondaemon threads close
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.viewer.addClient(client)
		

#Starts logger for debugger; not currently used, but I'm leaving it incase I need it later
logging.basicConfig(filename = 'tweeteor.log', level=logging.DEBUG, format='[%(levelname)s] (%(threadName)s) %(message)s')
pygame.init()
config = SafeConfigParser()
config.read('server.conf')
credentials = b64encode(config.get('auth', 'key') + ':' + config.get('auth', 'secret')) #Creates credentials for twitter api
searcher = Searcher(credentials)
searcher.start()
view = Viewer(searcher)
view.start()
address = ('', config.getint('connection', 'port'))
server = Server(address, view)
server.start()
inHandler = Controller(searcher)
inHandler.start()
