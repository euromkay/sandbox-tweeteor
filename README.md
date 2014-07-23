Tweeteor
========

A program for the Meteor linux cluster that displays tweets on the screen.
In order for this program to work, you must first make a file called "auth.py" with two variables in it: key and secret. These variables should be your twitter api key and secret, respectively. All files except client.py go on the computer acting as the server, while only constants.py and client.py go on the client. To start the program, run main.py on the server, then run client.py on the client(s). To change the size of the individual windows, or the number of windows per column/row, alter the constants.py module.
