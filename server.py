"""Handles communication between server process and clients."""
import json
import logging
from socket import socket, error as SocketError
from threading import Thread, Lock

from constants import WIN_SIZE, SCR_SIZE


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
        self.msg = ''
        self.msg_lock = Lock()
        # Daemon threads automatically die when no other threads
        # are left in a process, making shutdown easier.
        self.setDaemon(True)

    def run(self):
        """
        Wait for incoming socket connections,
        and add all to the client list.
        """
        while True:
            logging.debug("running")
            (client, _) = self.sock.accept()
            self.add_client(client)

    def send(self, msg):
        """Send a message to all connected clients."""
        with self.msg_lock:
            # msg is cached to be used as a "welcom message"
            # for new clients.
            self.msg = msg
        with self.client_lock:
            for client in self.clients:
                Server.send_to_client(client, msg)

    def add_client(self, client):
        """
        Setup connection with client, and add it to the client list.

        The client is sent the window and screen sizes,
        and a "welcome message", which is the last message sent to all clients.
        This welcome message prevents the client from having to wait
        for the next send, which make take several seconds.
        """
        with self.client_lock:
            # the recvs are used to wait for the client to acknowledge
            # that it recieved the message.
            client.send(json.dumps(WIN_SIZE))
            client.recv(3)
            client.send(json.dumps(SCR_SIZE))
            client.recv(3)
            with self.msg_lock:
                Server.send_to_client(client, self.msg)
            self.clients.append(client)

    @staticmethod
    def send_to_client(client, msg):
        """Send a message to a specific client."""
        try:
            # The client can't recieve all the data in one go,
            # so I have to tell it how much data to wait for.
            client.send(str(len(msg)))
            logging.debug('sending ' + str(len(msg)) + ' bytes')
            # waiting for acknowledgement
            client.recv(3)
            client.sendall(msg)
            client.recv(4)  # waiting to keep the client and server in sync
        except SocketError:
            pass
