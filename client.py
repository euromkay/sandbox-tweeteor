import json
import sys
import logging
from socket import socket
from threading import Thread, Event
from ConfigParser import SafeConfigParser

import pygame

from tweet import decode_tweet

# Constants
TWITTER_BLUE = pygame.Color(154, 194, 223)


class Client(Thread):

    def __init__(self, address, coords, exit):
        Thread.__init__(self, name='Client')
        pygame.display.set_caption(
            str(coords[0]) + "-" + str(coords[1]))
        self.coords = self.x, self.y = coords
        self.exit = exit
        self.sock = socket()
        self.sock.connect(address)
        # This represents the window belonging to the client
        self.window = pygame.display.set_mode(json.loads(self.sock.recv(128)))
        self.sock.send('ACK')
        # This represents the whole screen (all the clients' windows together)
        self.screen = pygame.Surface(json.loads(self.sock.recv(128)))
        self.sock.send('ACK')

    def run(self):
        try:
            while not exit.is_set():
                length = int(self.sock.recv(1024))
                self.sock.send('ACK')  # Tells server that it got the length
                msg = self.sock.recv(2048)
                # Calls recv multiple times to get the entire message
                while len(msg) < length:
                    msg += self.sock.recv(2048)
                self.sock.send('done')
                msg = msg[0:length]  # cut off the extra bytes
                if msg == 'exit':
                    break
                tweets = json.loads(msg, object_hook=decode_tweet)
                self.update_screen(tweets)
                pygame.display.update()
        finally:
            self.sock.close()
            exit.set()

    def update_screen(self, tweets):
        self.window.fill(TWITTER_BLUE)
        width, height = self.window.get_width(), self.window.get_height()
        area = pygame.Rect(
            self.coords[0] * width,
            self.coords[1] * height,
            width,
            height)
        for tweet in tweets:
            if tweet.rect.colliderect(area):
                tweet.rect.x -= area.x
                tweet.rect.y -= area.y
                self.window.blit(tweet.get_surface(), tweet.rect)

if __name__ == "__main__":
    logging.basicConfig(
        filename='log',
        level=logging.DEBUG,
        format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
    config = SafeConfigParser()
    config.read('config')
    address = (config.get('connection', 'address'),
               config.getint('connection', 'port'))
    # Uses coords from file if in auto mode, otherwise asks user for coords
    coords = (int(sys.argv[1]), int(sys.argv[2]))
    exit = Event()  # Event for coordinating shutdown
    try:
        pygame.init()
        client = Client(address, coords, exit)
        client.start()
        while not exit.is_set():
            # Exits if window was closed, and tells Client thread to close
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit.set()
                    client.join()
                    break
            # This else block executes as long as the for loop did not break
            # (e.g. the program is not shutting down)
            else:
                pygame.time.wait(10)
    finally:
        pygame.quit()
