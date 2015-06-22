"""
Constants read from or created based on the configuration file.

Contains the following constants:
    WIN_WIDTH - The width of a client's window.
    WIN_HEIGHT - The height of a client's window.
    WIN_SIZE - a tuple containing a client's window's width and height.
    WIN_PER_ROW - The number of clients in each row of Tweeteor.
    WIN_PER_COLUMN - The number of clients in each column of Tweeteor.
    SCR_WIDTH - The width of Tweeteor's display.
    SCR_HEIGHT - The height of Tweeteor's display.
    SCR_SIZE - a tuple containing the width and height of Tweeteor's display.

All dimensions are in pixels.
"""
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('config')
WIN_WIDTH = config.getint('window', 'width')
WIN_HEIGHT = config.getint('window', 'height')
WIN_SIZE = (WIN_WIDTH, WIN_HEIGHT)
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_WIDTH = WIN_WIDTH * WIN_PER_ROW
SCR_HEIGHT = WIN_HEIGHT * WIN_PER_COLUMN
SCR_SIZE = (SCR_WIDTH, SCR_HEIGHT)
