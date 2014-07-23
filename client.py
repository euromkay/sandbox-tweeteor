from socket import *
from base64 import *
from threading import Thread
from pygame.locals import *
from constants import *
import pygame, sys, json

white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)

class Client(Thread):
	def __init__(self, address, coords):
		Thread.__init__(self)
		pygame.init()
		self.coords = self.x, self.y = coords
		self.sock = socket()
		self.sock.connect(address)
		self.sock.send(json.dumps(self.coords))
		self.screen = pygame.display.set_mode(WIN_SIZE)
	def run(self):
		while True:
			msg = self.sock.recv(1024)
			if msg == 0:
				self.sock.close()
				pygame.quit()
				sys.exit()
			length = int(msg)
			self.screen.fill(white)
			self.sock.send('ACK')
			s = self.sock.recv(2048)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(2048)
			self.sock.send('done')
			s = s[0:length]#cut off the extra bytes
			l = json.loads(s)
			self.screen.blit(pygame.image.fromstring(b64decode(l[0]), l[1], 'RGBA'), (0, 0))
			pygame.display.update()
address = (raw_input("Enter server address: "), int(raw_input("Enter port number: ")))
coords = (int(raw_input('Enter X: ')), int(raw_input('Enter Y: ')))
client = Client(address, coords)
client.start()
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	pygame.time.wait(10)
