#!/usr/bin/python2
"""Starts the Tweeteor server."""
import logging
import os
from ConfigParser import SafeConfigParser

from controller import Controller
from searcher import Searcher

if __name__ == "__main__":
    logging.basicConfig(
        filename='log',
        level=logging.DEBUG,
        format="[%(asctime)s : %(levelname)s] [%(threadName)s] %(message)s")
    config = SafeConfigParser()
    config.read('config')
    # An exception is thrown if you acces a non-existant directory,
    # so we make sure they exist here
    image_cache = os.path.join("cache", "images")
    tweet_cache = os.path.join("cache", "tweets")
    required_dirs = [image_cache, tweet_cache]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
    # Using '' as the hostname allows the socket to bind to
    # its correct address, without you needing to know exactly what
    # that address is.
    address = ('', config.getint('connection', 'port'))
    api_key = config.get('auth', 'key')
    api_secret = config.get('auth', 'secret')
    searcher = Searcher(api_key, api_secret, address)
    searcher.start()
    controller = Controller(searcher)
    controller.start()
    for user in ['rpwagner', 'NSF_CISE', 'iSupercomputing', 'HPCwire', 'HPCatDell', 'HPC_Guru', 'insidehpc', 'Internet2', 'Livermore_Comp', 'DonaLCrawford', 'OLCFGOV', 'AeonComputing', 'Intersect360', 'NASA_Supercomp', 'intel', 'NERSC', 'mellanoxtech', 'cray_inc', 'NCSAatIllinois', 'IntelHPC', 'WorDS_SDSC', 'SDSC_UCSD']:#, 'XSEDEscience', 'TACC', 'psc_live', ]:
        searcher.add_user(user)
