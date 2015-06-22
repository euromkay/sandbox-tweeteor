"""
Used for downloading images from the web.
Images are cached to decrease network usage, and avoid any API rate limits.
"""
import os

import pygame
import requests


def get_image(url):
    """
    Retrieve a Surface containing the image at the requested url.
    Throws an IOError if no image was found.

    Once an image is downloaded, it is saved to the images/ directory.
    If a previously downloaded image is requested again, it is retrieved
    from the images/ directory, instead of being redownloaded.
    """
    # os.path.join is used to be cross-platform;
    # this code may one day run on Windows.
    directory = os.path.join("cache", "images")
    # Slashes are removed from the image name to avoid file naming problems.
    filename = os.path.join(directory, url.replace('/', ''))
    if not os.path.isfile(filename):
        img_request = requests.get(url)
        if img_request.status_code == 200:
            with open(filename, mode="w") as f:
                f.write(img_request.content)
        else:
            error_message = (str(img_request.status_code) +
                             " Error occured: " +
                             img_request.text)
            raise IOError(error_message)
    return pygame.image.load(filename)
