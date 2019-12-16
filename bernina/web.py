from bottle import Bottle, get, post, run, static_file, request, response, redirect
from doreah.pyhp import file as pyhpfile
from . import db
#import auth
from doreah import auth, settings, packageutils
import pkg_resources
import os


MAIN_PORT = settings.get_settings("PORT")
HOST = settings.get_settings("HOST")
THREADS = 12

WEBFOLDER = pkg_resources.resource_filename(__name__,"web")
STATICFOLDER = pkg_resources.resource_filename(__name__,"static")
DATAFOLDER = packageutils.pkgdata()

pthjoin = os.path.join

def generate_css():
	import lesscpy
	from io import StringIO
	less = ""
	for f in os.listdir(pthjoin(STATICFOLDER,"less")):
		with open(pthjoin(STATICFOLDER,"less",f),"r") as lessf:
			less += lessf.read()

	css = lesscpy.compile(StringIO(less),minify=True)
	return css

css = generate_css()

def server_handlers(server):


	@server.get("/style.css")
	def get_css():
		response.content_type = 'text/css'
		return css

	@server.get("/<name>.<ext>")
	def file(name,ext):
		return static_file(ext + "/" + name + "." + ext,root=STATICFOLDER)


	@server.get("/")
	def start():
		if auth.check(request):
			result = pyhpfile(os.path.join(WEBFOLDER,"main.pyhp"),{"db":db})
		else:
			#result = pyhpfile("web/login.pyhp",{"db":db,"auth":auth})
			result = auth.get_login_page(stylesheets=["/style.css"])

		return result
