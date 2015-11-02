#!/usr/bin/python2
"""
Recieves and displays content from the server.

When ran as a script, the first parameter is the x coordinate
of the client, and the second is the y parameter.
"""
import json
import sys
import logging
from socket import socket
from threading import Thread, Event
from ConfigParser import SafeConfigParser

import pygame

import config2

from tweet import decode_tweet

TWITTER_BLUE = pygame.Color(0, 0, 0)


class Client(Thread):
    """
    Dedicated thread for displaying content from the server.
    The client is relatively dumb, in that it does no processing of it's own,
    aside from checking which tweets to display.
    """

    def __init__(self, address, coords, exit):
        """
        Creates a Client which will connect to a server at the given address,
        and displays Tweets that are in the "cell" represented by coords.
        Exit is used to coordinate shutdown with the script at the bottom
        of this module.

        Coordinates start at (0,0) in the upper left, and increase as you
        move right/down, just as in Pygame.
        """
        Thread.__init__(self, name='Client')
        # Setting the coordinates as a caption makes
        # setting up Tweeteor easier, especially when
        # testing on your own computer.
        pygame.display.set_caption(
            str(coords[0]) + "-" + str(coords[1]))
        self.coords = self.x, self.y = coords
        self.exit = exit
        self.sock = socket()
        self.sock.connect(address)
        coords = json.loads(self.sock.recv(128))
        mode = config2.config['mode']
        self.window = pygame.display.set_mode(coords, mode, 0)
        self.sock.send('ACK')

    def run(self):
        """
        Connect to the server, and display the Tweets recieved."""
        try:
            while not exit.is_set():
                length = int(self.sock.recv(1024))
                self.sock.send('ACK')  # Tells server that it got the length
                msg = self.sock.recv(2048)
                # We have to call recv multiple times
                # to ensure we get the entire message.
                while len(msg) < length:
                    msg += self.sock.recv(2048)
                self.sock.send('done')
                # Recv sometimes sends extra trash bytes at the end,
                # so we just remove them.
                msg = msg[0:length]
                if msg == 'exit':
                    break
                tweets = json.loads(msg, object_hook=decode_tweet)
                self.update_screen(tweets)
                pygame.display.update()
        except:
            # This block does not actually handle the error, only log it.
            # That's why we re-raise the error, so that important errors
            # are not silenced.
            logging.exception("Fatal Exception Thrown")
            raise
        # The finally block guarantees that clients shutdown properly.
        # Before this was in place, clients would freeze upon an error,
        # forcing you to manually close them all.
        finally:
            exit.set()

    def update_screen(self, tweets):
        """
        Place tweets on the screen, but only if they are actually
        within the client's coordinates.
        """
        self.window.fill(TWITTER_BLUE)
        width, height = self.window.get_width(), self.window.get_height()
        # This gives us the location of our window, in regards to
        # the rest of Tweeteor.
        area = pygame.Rect(
            self.coords[0] * width,
            self.coords[1] * height,
            width,
            height)
        for tweet in tweets:
            if tweet.rect.colliderect(area):
                # We have to convert the tweets global coordinates
                # to our own window's coordinates, or else they appear
                # in the wrong place.
                tweet.rect.x -= area.x
                tweet.rect.y -= area.y
                self.window.blit(tweet.get_surface(), tweet.rect)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print """
              Usage: python2 client.py x y
              x is the x coordinate of the client,
                with 0 all the way to the left.
              y is the y coordinate of the client,
                with 0 all the way at the top.
              """
        sys.exit()
    logging.basicConfig(
        filename='log',
        level=logging.DEBUG,
        format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
    config = SafeConfigParser()
    config.read('config')
    address = (config.get('connection', 'address'),
               config.getint('connection', 'port'))
    coords = (int(sys.argv[1]), int(sys.argv[2]))
    exit = Event()  # Event for coordinating shutdown
    try:
        pygame.init()
        client = Client(address, coords, exit)
        client.start()
        while not exit.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit.set()
                    client.join()
                    break
            # This else block executes as long as the for loop did not break
            # (e.g. the program is not shutting down)
            else:
                pygame.time.wait(10)
    except:
        # This block does not actually handle the error, only log it.
        # That's why we re-raise the error, so that important errors
        # are not silenced.
        logging.exception("Fatal Exception Thrown")
        raise
    finally:
        pygame.quit()
