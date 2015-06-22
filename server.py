"""Handles communication between server process and clients."""
import json
import logging
from socket import socket, error as SocketError
from threading import Thread, Lock

from constants import WIN_SIZE


class Server(Thread):
    """
    A dedicated thread for recieving incoming connections by clients.
    Also contains methods for sending messages to one or all
    connected clients.
    """

    def __init__(self, address):
        """Creates a server listening at the given address."""
        Thread.__init__(self, name='Server')
        self.sock = socket()
        self.sock.bind(address)
        self.sock.listen(5)
        self.clients = []
        self.client_lock = Lock()
        # Cache of last sent message. Used so that newly connected clients
        # do not have to wait for the next send
        # (which may take several seconds).
        self.cached_msg = ''
        self.msg_lock = Lock()
        # Daemon threads automatically die when no other threads
        # are left in a process, making shutdown easier.
        self.setDaemon(True)

    def run(self):
        """
        Accept incoming connections from clients.
        """
        try:
            while True:
                (client, _) = self.sock.accept()
                self.add_client(client)
        except:
            # This block does not actually handle the error, only log it.
            # That's why we re-raise the error, so that important errors
            # are not silenced.
            logging.exception("Fatal Exception Thrown")
            raise

    def send(self, message):
        """
        Send a message to all connected clients.
        """
        with self.msg_lock:
            self.cached_msg = message
        with self.client_lock:
            for client in self.clients:
                Server.send_to_client(client, message)

    def add_client(self, client):
        """
        Setup connection with client.
        """
        with self.client_lock:
            # the recv is used to wait for the client to acknowledge
            # that it recieved the message.
            client.send(json.dumps(WIN_SIZE))
            client.recv(3)
            with self.msg_lock:
                Server.send_to_client(client, self.cached_msg)
            self.clients.append(client)

    @staticmethod
    def send_to_client(client, message):
        """Send a message to a specific client."""
        try:
            # The client can't recieve all the data in one go,
            # so I have to tell it how much data to wait for.
            client.send(str(len(message)))
            # waiting for acknowledgement
            client.recv(3)
            client.sendall(message)
            client.recv(4)  # waiting to keep the client and server in sync
        except SocketError:
            logging.exception("Error in sending to client")
