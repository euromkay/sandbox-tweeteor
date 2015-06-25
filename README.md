Tweeteor
========

Meteor's social media screen saver. Searches Twitter based on input from the
user, and displays the tweets across multiple computers.

Dependencies
------------

* Python 2.7
* Pygame
* Requests

Installation
------------

1. Install all dependencies.
2. Clone this repository.
3. create a copy of config.example, and rename it to config.
4. Place your Twitter API key and API secret in the auth section of config.
5. Change the address field in config to the IP address that the server
   will run on.
6. If you are on a Unix-like system, set main.py, client.py,
   and clientrunner.sh as executable.

Usage
-----

1. Run main.py on the server computer.
2. Run client.py on all the clients. If the clients are all on one
   computer (e.g. during testing), you can just run clientrunner.sh instead.
3. If you want to change the number of windows, their sizes,
   or other settings, edit config.
