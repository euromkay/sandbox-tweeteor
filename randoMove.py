###How to use###

#Use initPic (profile picture)(you could also just blit the image onto the mover) and initRan outside
#of the main pygame loop. Then use makeMove inside of the main pygame loop to move the
#mover

#Essentially what this does is it creates the position of the mover and a randomly generated point
#outside of the loop then inside the loop the mover moves one pixel torwards the randomly
#generated point then once it gets there generates a new random point. In order to move more
#than one pixel a frame the program checks if the randomly generated point is divisible by the
#amount of pixels moved


#initPic(instance number, profile picture filename)
#font(fontname, fontsize)
#makeMove(username string, message string, font function, instance, x instance, y instance, xran instance, yran instance)

import pygame, sys, time, random, urllib, urllib2, os, Image
from pygame.locals import *
from random import *

def initPic(d,inputPic=None):
    global picDict
    picDict = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    if inputPic==None:
        getPic=urllib.urlretrieve('http://placekitten.com/300/300' ,'toBeResized.png')
        inputPic = 'toBeResized.png'
    resize = Image.open(inputPic)
    r = resize.resize((100,100), Image.BILINEAR)
    r.save("pic"+str(d)+".png")
    picDict[d] = pygame.image.load("pic"+ str(d) +".png").convert() #Import your porn pics
    os.remove('toBeResized.png')
    os.remove('pic'+str(d)+'.png')
    
def initRan(instance):
    global rectLength, c
    rectLength=0
    c=1 #Moving c pixels per frame
    global x,y,ranx,rany, n
    #probably should append to my lists huh...
    x = [randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength)]
    y = [randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30)]
    ranx = [randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength),randrange(1 ,a-rectLength)]
    rany = [randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30),randrange(1,b-30)]
    def checkx(instance):
        global x,y
        while x[g]%c !=0:
            x[g] = randrange(1 ,a-rectLength)
    def checky(instance):
        global x,y
        while y[j]%c != 0:
            y[j] = randrange(1,b-30)
    def checkranx(instance):
        global a, b, n,ranx,rany
        while ranx[g]%c !=0:
            ranx[g] = randrange(1 ,a-rectLength)
        if ranx[g]%c == 0:
            n = 1
    def checkrany(instance):
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
        
def makeMove(instance):  
    global ranx, rany, n, x, y
    rectLength = len(message) * 9 #length of the whole message string so that the text doesnt float outside of the surface
    if n == 1:
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
    while True: 
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
        
def event():
    global mouseX, mouseY
    for event in pygame.event.get(): #Loop for accepting user input
            if event.type == QUIT: #Lets you quit
                pygame.quit()
                sys.exit()       
            elif event.type == MOUSEMOTION: #Move mouse x and y to mouse position
                mouseX, mouseY = event.pos
                
#initPic(0 , 'picture0')
#initPic(1 , 'picture1')
#initRan(0)
#initRan(1)
#while True:
    #makeMove(0)
    #makeMove(1)
