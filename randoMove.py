############
# How to use  #
############

#init() Is to be called outside of the pygame loop with its options being however many instances (int) of floating movers you
#need. makeMove() Should then be used inside the main pygame loop for however many instances you want. 

#Essentially what this does is it creates the position of the mover and a randomly generated point
#outside of the loop then inside the loop the mover moves one pixel torwards the randomly
#generated point then once it gets there it generates a new random point. In order to move more
#than one pixel a frame the program checks if the randomly generated point is divisible by the
#amount of pixels moved

import pygame, sys, time, random, urllib, urllib2, os, Image
from pygame.locals import *
from random import *

picList, x, y ,ranx ,rany = [],[],[],[],[] #Storage for pictures and mover location
rectLength=0 
c=1 #speed- Pixels to move per frame

def init(instance): #For initializing the picture and coordinate stuff for however many "instance"'s we need
    global ranx,rany,x,y
    n=0
    while n != instance:
        initPic(n)
        initRan(n)
        print n
        n += 1    

def initPic(d,inputPic=None): #Takes a picture, resizes it then makes it into a pygame object
    global picList
    if inputPic==None:
        getPic=urllib.urlretrieve('http://placekitten.com/300/300' ,'toBeResized.png')
        inputPic = 'toBeResized.png'
    resize = Image.open(inputPic)
    r = resize.resize((100,100), Image.BILINEAR)
    r.save("pic"+str(instance)+".png")
    picList.extend([ pygame.image.load("pic"+ str(instance) +".png").convert()]) 
    os.remove('toBeResized.png')
    os.remove('pic'+str(instance)+'.png')
    
def initRan(instance): #Creates the position of mover and the random coordinate of where it will move to
    global x,y,ranx,rany,n
    x.append(randrange(1 ,a-rectLength))
    y.append(randrange(1,b-30))
    ranx.append(randrange(1 ,a-rectLength))
    rany.append(randrange(1,b-30))
    while x[instance]%c !=0:
        x[instance] = randrange(1 ,a-rectLength)
    while y[instance]%c != 0:
        y[instance] = randrange(1,b-30)
    while ranx[instance]%c !=0:
        ranx[instance] = randrange(1 ,a-rectLength)
    if ranx[instance]%c == 0:
        n = 1
    while rany[instance]%c != 0:
        rany[instance] = randrange(1,b-30)
    if rany[instance]%c == 0:
        n = 1   
        
def makeMove(instance):  #Move mover 'c' amount of pixels torwards random coordinate. Must be inside main pygame loop
    global x,y,ranx,rany,n
    rectLength = len(message) * 9 #length of the whole message string so that the text doesnt float outside of the surface

    if n == 1: #New random point making logic
        rany[instance] = randrange(1 ,b-30)
        while rany[instance]%c !=0:
            rany[instance] = randrange(1 ,b-30)
        if rany[instance]%c != 0:
            n = 1
        ranx[instance] = randrange(1 ,a-rectLength)
        while ranx[instance]%c != 0:
            ranx[instance] = randrange(1 ,a-rectLength)
        if ranx[instance]%c != 0:
            n = 1
        n = 2
        
    while True: #Moving torwards coordinate logic
        if x[instance] == ranx[instance]: #If x is equal to the randomly generated x then it will create a new one and print it
            ranx[instance] = randrange(1,a-rectLength)
            while ranx[instance]%c != 0:
                ranx[instance] = randrange(1,a-rectLength)
            print "x ", ranx[instance]
            continue
        if y[instance] == rany[instance]: #Same as x
            rany[instance] = randrange(1 ,b-30)
            while rany[instance]%c !=0:
                rany[instance] = randrange(1 ,b-30)
            print "y ", rany[instance]
            continue
        if x[instance] != ranx[instance] and x[instance] > ranx[instance]: #If x is not equal to ranx then move it torwards ranx
            x[instance] -= c
        elif x[instance] != ranx[instance] and x[instance] < ranx[instance]:
            x[instance] += c
        if y[instance] != rany[instance] and y[instance] > rany[instance]:
            y[ydict] -= c
        elif y[instance] != rany[instance] and y[instance] < rany[instance]:
            y[instance] += c
        break
    surface.blit(picDict[instance], (x[instance]-110,y[instance]))
    mover = pygame.Rect((x[instance],y[instance]), (1,1)) #Coordinates: (X,Y,Length,Height) 
    mover.topleft = (x[instance],y[instance]) #topleft 
    #surface.blit(messagestringandwhatnot, mover) an example
        
def event(): #If we want pygame events
    global mouseX, mouseY
    for event in pygame.event.get(): #Loop for accepting user input
            if event.type == QUIT: #Lets you quit
                pygame.quit()
                sys.exit()       
            elif event.type == MOUSEMOTION: #Move mouse x and y to mouse position
                mouseX, mouseY = event.pos
                
    
#########
# Example #
#########
                
#init(2) 
    
#while True:
    #makeMove(0)
    #makeMove(1)
