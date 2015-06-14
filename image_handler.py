"""Used for downloading images from the web."""
import os

import pygame
import requests

def get_image(url):
    """
    Retrieve an image from the web, or local cache.
    
    Once an image is downloaded, it is saved to the images/ directory.
    If a previously downloaded image is requested again, it is retrieved
    from the images/ directory, instead of being redownloaded.
    """
    #os.path.join is used to be cross-platform;
    #this code may one day run on Windows. Slashes are removed
    #from the image name to avoid file naming problems.
    filename = os.path.join("images", url.replace('/', ''))
    #Only download the image if it is not cached yet
    if not os.path.isfile(filename):
        img_request = requests.get(url)
        if img_request.status_code == 200:#make sure the link worked
            f = open(filename, mode = 'w')
            #Saves image in temp file so it only has to be downloaded once
            f.write(img_request.content)
            f.close()
        else:
            raise Error('URL Invalid!') 
    return pygame.image.load(filename)
