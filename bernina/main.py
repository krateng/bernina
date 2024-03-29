import os

from bottle import Bottle, run
import waitress
from . import web
from . import db
from threading import *
import time
from doreah.settings import get_settings
from doreah import auth
#import auth
import signal


HOST, PORT = get_settings("HOST","PORT")
THREADS = 12







def graceful_exit(sig=None,frame=None):
	print("Server shutting down...")
	db.save_database()
	os._exit(42)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)


server = Bottle()

db.api.mount(server=server)
auth.authapi.mount(server=server)
web.server_handlers(server=server)

waitress.serve(server,host=HOST,port=PORT,threads=THREADS)
