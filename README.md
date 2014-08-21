Tweeteor
========

Meteor's social media screen saver.
In order for this program to work, you must first add your twitter api key and secret to server.conf. 
All files except client.py and client.conf go on the server, while only client.py and client.conf go on the client.
To start the program, run main.py on the server, then run client.py on the client(s). 
To change the port and address used for communication, edit server.conf and client.conf.
To change the size and number of windows, edit server.conf.
To change font size, edit client.conf.
Because all the clients share a filesystem, the autocoordinate system does not work. Leave the setting as false.
