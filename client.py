from socket import *
from base64 import *
from threading import Thread, Event
from pygame.locals import *
from constants import *
from ConfigParser import SafeConfigParser
import pygame, sys, json, threading

class Client(Thread):
	def __init__(self, address, coords, exit):
		Thread.__init__(self, name = 'Client')
		pygame.init()
		self.coords = self.x, self.y = coords
		self.sock = socket()
		self.sock.connect(address)
		self.sock.send(json.dumps(self.coords))
		self.screen = pygame.display.set_mode(json.loads(self.sock.recv(128))) #Gets the window size from the server
		self.exit = exit
	def run(self):
		while True:
			#Exits if window was closed
			if exit.isSet():
				self.sock.close()
				pygame.quit()
				sys.exit()
			msg = self.sock.recv(1024)
			#Exits if server tells client to close. That makes two ways to close the client
			if msg[0:4] == 'exit':
				self.sock.close()
				exit.set()
				return
			length = int(msg)
			self.screen.fill(white)
			self.sock.send('ACK') #Tells server that it got the length
			s = self.sock.recv(2048)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(2048)
			self.sock.send('done')
			s = s[0:length]#cut off the extra bytes
			l = json.loads(s)
			self.screen.blit(pygame.image.fromstring(b64decode(l[0]), l[1], 'RGBA'), (0, 0)) #l[0] is the string representing the surface, and l[1] is the size of the surface (should match client's size)
			pygame.display.update()

config = SafeConfigParser()
config.read('client.conf')
address = (config.get('connection', 'address'), config.getint('connection', 'port'))
#Uses coords from file if in auto mode, otherwise asks user for coords
if config.getboolean('coordinates', 'auto'):
	coords = (config.getint('coordinates', 'x'), config.getint('coordinates', 'y'))
else:
	coords = (int(raw_input('X: ')), int(raw_input('Y: ')))
exit = Event() #Event for coordinating shutdown
client = Client(address, coords, exit)
client.start()
while True:
	#Exits if Client thread already exited
	if exit.isSet():
		pygame.quit()
		sys.exit()
	#Exits if window was closed, and tells Client thread to close
	for event in pygame.event.get():
		if event.type == QUIT:
			exit.set()
			break
	#This else block executes as long as the for loop did not break (the program is not shutting down)
	else:
		pygame.time.wait(10)
		continue
	break #Only executes if earlier break was called
