from controller import *
from searcher import *
from server import *
from ConfigParser import SafeConfigParser
from base64 import b64encode
import logging

#Starts logger for debugger
logging.basicConfig(filename = 'server.log', level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s')
config = SafeConfigParser()
config.read('server.conf')
		
address = ('', config.getint('connection', 'port'))
credentials = b64encode(config.get('auth', 'key') + ':' + config.get('auth', 'secret')) #Creates credentials for twitter api
searcher = Searcher(credentials, address)
searcher.start()
inHandler = Controller(searcher)
inHandler.start()
