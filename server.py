from socket import *
from ConfigParser import SafeConfigParser
from threading import Thread, Lock
import sys, json, logging

#Constants- DO NOT EDIT! change server.conf instead
config = SafeConfigParser()
config.read('server.conf')
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = config.getint('window', 'width'), config.getint('window', 'height')
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_SIZE = SCR_WIDTH, SCR_HEIGHT = WIN_WIDTH * WIN_PER_ROW, WIN_HEIGHT * WIN_PER_COLUMN

class Server(Thread):
	def __init__(self, address, sender):
		Thread.__init__(self, name = 'Server')
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.clients = []
		self.clientLock = Lock()
		self.sender = sender
		self.msg = ''
		self.msgLock = Lock()
		self.setDaemon(True)
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.addClient(client)
	def send(self, msg):
		with self.clientLock:
			for client in self.clients:
				sendToClient(client, msg)
	def addClient(self, client):
		msg = self.sender.getWelcomeData()
		with self.clientLock:
			client.send(json.dumps(WIN_SIZE))
			client.recv(3)
			client.send(json.dumps(SCR_SIZE))
			client.recv(3)
			sendToClient(client, msg)
			self.clients.append(client)
def sendToClient(client, msg):
	try:
		client.send(str(len(msg))) #The client can't recieve all the data in one go, so I have to tell it how much data to wait for
		logging.debug('sending ' + str(len(msg)) + ' bytes')
		client.recv(3)
		client.sendall(msg)
		client.recv(4) #waiting to keep the client and server in sync
	except:
		pass
