from ConfigParser import SafeConfigParser

# Constants- DO NOT EDIT! change server.conf instead
config = SafeConfigParser()
config.read('config')
WIN_WIDTH = config.getint('window', 'width')
WIN_HEIGHT = config.getint('window', 'height')
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT
WIN_PER_ROW = config.getint('window', 'win_per_row')
WIN_PER_COLUMN = config.getint('window', 'win_per_col')
SCR_WIDTH = WIN_WIDTH * WIN_PER_ROW
SCR_HEIGHT = WIN_HEIGHT * WIN_PER_COLUMN
SCR_SIZE = SCR_WIDTH, SCR_HEIGHT
