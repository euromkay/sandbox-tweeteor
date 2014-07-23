###How to use###

#Use initPic (profile picture) and initRan outside of the main pygame loop. Then use makeMove
#inside of the main pygame loop to move the object to be moved around.

#Essentially what this does is it creates the position of the object and the randomly generated point
#outside of the loop then inside the loop it moves one pixel torwards it


#initPic(instance number, profile picture filename)
#font(fontname, fontsize)
#makeMove(username string, message string, font function, instance, x instance, y instance, xran instance, yran instance)

import pygame, sys, time, random, urllib, urllib2, os, Image, win32gui
from pygame.locals import *
from random import *
from win32gui import *

c = 1 #Speed of floating object
picDict = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
rectLength=0

def message(msg=None):
    global rectLength
    if msg == None:
        msg = "Are you being cayoot today?" #A-Am I cool yet
    rectLength = len(msg) * 9
    return msg
def font(fontName=None, fontSize=None):
    if fontName == None:
        font = pygame.font.Font('Cutie Patootie.ttf', 26) #Create a font for your text. Font then font size
    elif fontSize == None:
        font = pygame.font.Font(fontName, 26) #Create a font for your text. Font then font size
    elif fontSize == None and fontName == None:
        font = pygame.font.Font('Cutie Patootie.ttf', 26) #Create a font for your text. Font then font size
    else:
        font = pygame.font.Font(fontName, fontSize) #Create a font for your text. Font then font size
    return font
def initPic(d,inputPic=None):
    global picDict
    if inputPic==None:
        getPic=urllib.urlretrieve('http://placekitten.com/300/300' ,'toBeResized.png')
        inputPic = 'toBeResized.png'
    resize = Image.open(inputPic)
    r = resize.resize((100,100), Image.BILINEAR)
    r.save("pic"+str(d)+".png")
    picDict[d] = pygame.image.load("pic"+ str(d) +".png").convert() #Import your porn pics
    os.remove('toBeResized.png')
    os.remove('pic'+str(d)+'.png')
    
def initRan():
    global x,y,ranx,rany, n
    x = {'x1': randrange(1 ,a-rectLength), 'x2': randrange(1 ,a-rectLength)}
    y = {'y1': randrange(1,b-30), 'y2':randrange(1,b-30)}
    ranx = {'ranx1': randrange(1 ,a-rectLength), 'ranx2': randrange(1 ,a-rectLength)}
    rany = {'rany1': randrange(1,b-30), 'rany2':randrange(1,b-30)}
    def checkx(g):
        global x,y
        while x[g]%c !=0:
            x[g] = randrange(1 ,a-rectLength)
    def checky(j):
        global x,y
        while y[j]%c != 0:
            y[j] = randrange(1,b-30)
    def checkranx(g):
        global a, b, n,ranx,rany
        while ranx[g]%c !=0:
            ranx[g] = randrange(1 ,a-rectLength)
        if ranx[g]%c == 0:
            n = 1
    def checkrany(j):
        global a, b, n,ranx,rany
        while rany[j]%c != 0:
            rany[j] = randrange(1,b-30)
        if rany[j]%c == 0:
            n = 1
    for k in x:
        checkx(k)
    for k in y:
        checky(k)
    for k in ranx:
        checkranx(k)
    for k in rany:
        checkrany(k)
        
def makeMove(username, msg,font,d,  xdict, ydict, ranxdict, ranydict):  
    global ranx, rany, n, x, y
    message = username + "- " + '"' + msg + '"'
    rectLength = len(message) * 9
    if n == 1:
        rany[ranydict] = randrange(1 ,b-30)
        while rany[ranydict]%c !=0:
            rany[ranydict] = randrange(1 ,b-30)
        if rany[ranydict]%c != 0:
            n = 1
        ranx[ranxdict] = randrange(1 ,a-rectLength)
        while ranx[ranxdict]%c != 0:
            ranx[ranxdict] = randrange(1 ,a-rectLength)
        if ranx[ranxdict]%c != 0:
            n = 1
        n = 2
    while True: 
        if x[xdict] == ranx[ranxdict]: #If x is equal to the randomly generated x then it will create a new one and print it
            ranx[ranxdict] = randrange(1,a-rectLength)
            while ranx[ranxdict]%c != 0:
                ranx[ranxdict] = randrange(1,a-rectLength)
            print "x ", ranx[ranxdict]
            continue
        if y[ydict] == rany[ranydict]: #Same as x
            rany[ranydict] = randrange(1 ,b-30)
            while rany[ranydict]%c !=0:
                rany[ranydict] = randrange(1 ,b-30)
            print "y ", rany[ranydict]
            continue
        if x[xdict] != ranx[ranxdict] and x[xdict] > ranx[ranxdict]: #If x is not equal to ranx then move it torwards ranx
            x[xdict] -= c
        elif x[xdict] != ranx[ranxdict] and x[xdict] < ranx[ranxdict]:
            x[xdict] += c
        if y[ydict] != rany[ranydict] and y[ydict] > rany[ranydict]:
            y[ydict] -= c
        elif y[ydict] != rany[ranydict] and y[ydict] < rany[ranydict]:
            y[ydict] += c
        break
    window.blit(picDict[d], (x[xdict]-110,y[ydict]))
    pygame.draw.rect(window, white, (x[xdict]-3,y[ydict],rectLength,30)) #Coordinates: (X,Y,Length,Height) 
    msgObj = font.render(message, 1, pinkColor) #makes a msg object to be blit onto the window. (Text, antialias or no(1,0), color)
    textPos = msgObj.get_rect() #Create an object surface to draw the text on. In this case we shall make a rectangle
    #textPos.center = window.get_rect().center #Center it. Other options are: topleft, top, left, centerx, bottom, width, and more
    textPos.topleft = (x[xdict],y[ydict]) #topleft example
    window.blit(msgObj, textPos) #blit the message onto the text positioner (empty rectangle)
        
def event():
    global mouseX, mouseY
    for event in pygame.event.get(): #Loop for accepting user input
            if event.type == QUIT: #Lets you quit
                pygame.quit()
                sys.exit()       
            elif event.type == MOUSEMOTION: #Move mouse x and y to mouse position
                mouseX, mouseY = event.pos

