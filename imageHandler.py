import os, pygame, requests

def getImage(url):
    filename = os.path.join("images", url.replace('/', ''))
    if os.path.isfile(filename):
        f = open(filename, 'r')
    else:
        imgRequest = requests.get(url)
        if imgRequest.status_code == 200:#make sure the link worked
            f = open(filename, mode = 'w')
            f.write(imgRequest.content)#Saves image in temp file so it only has to be downloaded once
            f.close()
        else:
            raise Error('URL Invalid!') 
    return pygame.image.load(filename)

def getSurface(id):
    filename = os.path.join("images", str(id) + ".png")
    return pygame.image.load(filename)
