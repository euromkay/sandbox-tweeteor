Tweeteor
========

Meteor's social media screen saver.
In order for this program to work, you must first add your twitter api key and secret to server.conf.
All files except client.py and client.conf go on the server, while only constants.py, client.py, and client.conf go on the client.
To start the program, run main.py on the server, then run client.py on the client(s). 
To change the port and address used for communication, edit server.conf and client.conf.
To change the size and number of windows, edit server.conf.
When you install Tweeteor on the actual Meteor cluster, change auto to True in client.conf/coordinates, and set the correct x and y coordinates for the window.
