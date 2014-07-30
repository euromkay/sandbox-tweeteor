from controller import *
from searcher import *
from threading import Thread, Lock
from socket import *
from ConfigParser import SafeConfigParser
from base64 import b64encode
import sys, logging

#Starts logger for debugger; not currently used, but I'm leaving it incase I need it later
logging.basicConfig(filename = 'server.log', level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
config = SafeConfigParser()
config.read('server.conf')
#Constants- DO NOT EDIT! change server.conf instead
BORDER_WIDTH = 10
BORDER_HEIGHT = 10
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = config.getint('window', 'width'), config.getint('window', 'height')
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_SIZE = SCR_WIDTH, SCR_HEIGHT = WIN_WIDTH * WIN_PER_ROW, WIN_HEIGHT * WIN_PER_COLUMN

class Server(Thread):
	def __init__(self, address):
		Thread.__init__(self, name = 'Server')
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.clients = []
		self.clientLock = Lock()
		self.msg = ''
		self.msgLock = Lock()
		self.setDaemon(True)
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.addClient(client)
	def send(self, msg):
		with self.msgLock:
			self.msg = msg
		with self.clientLock:
			for client in self.clients:
				try:
					client.send(str(len(msg))) #The client can't recieve all the data in one go, so I have to tell it how much data to wait for
					logging.debug('sending ' + str(len(msg)) + ' bytes')
					client.recv(3)
					client.sendall(msg)
					client.recv(4) #waiting to keep the client and server in sync
				except:
					pass
	def addClient(self, client):
		with self.msgLock:
			msg = self.msg
		with self.clientLock:
			client.send(json.dumps(WIN_SIZE))
			client.recv(3)
			client.send(json.dumps(SCR_SIZE))
			client.recv(3)
			client.send(str(len(msg))) #The client can't recieve all the data in one go, so I have to tell it how much data to wait for
			logging.debug('sending ' + str(len(msg)) + ' bytes')
			client.recv(3)
			client.sendall(msg)
			client.recv(4) #waiting to keep the client and server in sync
			self.clients.append(client)
		
address = ('', config.getint('connection', 'port'))
server = Server(address)
server.start()
credentials = b64encode(config.get('auth', 'key') + ':' + config.get('auth', 'secret')) #Creates credentials for twitter api
searcher = Searcher(credentials, server)
searcher.start()
inHandler = Controller(searcher)
inHandler.start()
