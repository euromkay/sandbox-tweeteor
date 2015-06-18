from socket import *
from tweet import *
from rectangle_handler import *
from pygame.locals import *
from threading import Thread, Event
from ConfigParser import SafeConfigParser
import pygame, sys, json, threading, logging

#Constants
BORDER_WIDTH = 20
BORDER_HEIGHT = 20
white = pygame.Color(255, 255, 255, 255)
black = pygame.Color(0, 0, 0, 255)
blue = pygame.Color(0, 0, 255, 255)
twitter_bg_blue = pygame.Color(154, 194, 223)
speechBubble = pygame.image.load('speech.png')

class Client(Thread):
	def __init__(self, address, coords, exit):
		Thread.__init__(self, name = 'Client')
		pygame.init()
                pygame.display.set_caption(str(coords[0]) + "-" + str(coords[1]))
		self.coords = self.x, self.y = coords
		self.exit = exit
		self.sock = socket()
		self.sock.connect(address)
		self.window = pygame.display.set_mode(json.loads(self.sock.recv(128))) #This represents the window belonging to the client
		self.sock.send('ACK')
		self.screen = pygame.Surface(json.loads(self.sock.recv(128))) #This represents the whole screen (all the clients' windows together)
		self.sock.send('ACK')
	def run(self):
		while True:
			logging.debug("running")
			#Exits if window was closed
			if exit.isSet():
				self.sock.close()
				pygame.quit()
				sys.exit()
			msg = self.sock.recv(1024)
			try:
				length = int(msg)
			except:
				logging.debug(msg)
			self.sock.send('ACK') #Tells server that it got the length
			s = self.sock.recv(2048)
			#Calls recv multiple times to get the entire message
			while len(s) < length:
				s += self.sock.recv(2048)
			self.sock.send('done')
			s = s[0:length]#cut off the extra bytes
			if s == 'exit':
				self.sock.close()
				exit.set()
				return
			tweets = json.loads(s, object_hook = decode_object)
			self.putTweetsOnScreen(tweets)
			pygame.display.update()
	#Placeholder method so you can change how the tweets are put on the screen(e.g. moving)
	def putTweetsOnScreen(self, tweetList):
		self.window.fill(twitter_bg_blue)
		width, height = self.window.get_width(), self.window.get_height()
                area = pygame.Rect(self.coords[0] * width, self.coords[1] * height, width, height)
                for tweet in tweetList:
                    if tweet.rect.colliderect(area):
                        tweet.rect.x -= area.x
                        tweet.rect.y -= area.y
                        self.window.blit(tweet.getSurface(), tweet.rect)

if __name__ == "__main__":
    logging.basicConfig(filename = 'client.log', level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
    config = SafeConfigParser()
    config.read('client.conf')
    address = (config.get('connection', 'address'), config.getint('connection', 'port'))
    #Uses coords from file if in auto mode, otherwise asks user for coords
    if config.getboolean('coordinates', 'auto'):
            coords = (config.getint('coordinates', 'x'), config.getint('coordinates', 'y'))
    else:
            coords = (int(sys.argv[1]), int(sys.argv[2]))
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
