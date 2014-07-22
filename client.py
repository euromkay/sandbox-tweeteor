from socket import *
from base64 import *
from threading import Thread
from pygame.locals import *
import pygame, sys, json

white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)

class Client(Thread):
	def __init__(self, address):
		Thread.__init__(self)
		pygame.init()
		self.sock = socket()
		self.sock.connect(address)
		self.screen = pygame.display.set_mode()
	def run(self):
		while True:
			self.screen.fill(white)
			length = int(self.sock.recv(2048))
			self.sock.send(' ')
			s = self.sock.recv(8192)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(8192)
			self.sock.send(' ')
			s = s[0:length]#cut off the extra bytes
			l = json.loads(s)
			self.screen.blit(pygame.image.fromstring(b64decode(l[0]), l[1], 'RGBA'), (0, 0))
			pygame.display.update()
address = (raw_input("Enter server address"), int(raw_input("Enter port number")))
client = Client(address)
client.start()
while True:
	for event in pygame.event.get():
        	if event.type == QUIT:
            		pygame.quit()
			sys.exit()
	pygame.time.wait(10)
