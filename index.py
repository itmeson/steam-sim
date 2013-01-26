#!/usr/bin/python

import sys

sys.stdout = sys.stderr
sys.path.append("/var/www/wilhall.com/steam/")

import atexit
import threading
import cherrypy

from webapp.settings import config
from webapp import main

main.config = config
main.configure()

cherrypy.config.update(config)

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
	cherrypy.engine.start(blocking=False)
	atexit.register(cherrypy.engine.stop)

cherrypy.tree.mount(None, config=config)
application = cherrypy.Application(None, script_name=None, config=config)