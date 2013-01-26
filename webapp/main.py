import cherrypy
import json

from mako.lookup import TemplateLookup

from authenticate import AuthHelper
from database import Database
from emailer import Emailer
from utils import timestamp

# PLaceholders for our helpers
logger = None
lookup = None
db = None
auth = None
emailer = None

# Called by /index.py
# Performs initial setup after helpers are injected into this module
# Necessary to later avoid circular imports
def configure(): 
	global lookup, db, auth, logger, emailer
	
	# Copy default logger
	logger = cherrypy.log
	
	# Initialize Emailer
	emailer = Emailer(config['emailer']['server'], config['emailer']['port'], config['emailer']['username'], config['emailer']['password'])
	
	# Configure TemplateLookup for mako
	lookup = TemplateLookup(directories=config['mako']['MAKO_DIRECTORIES'], default_filters=['decode.utf8'], input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
	
	# Initialize Database wrapper class
	db = Database(config['db']['DB_HOST'], config['db']['DB_USERNAME'], config['db']['DB_PASSWORD'], config['db']['DB_NAME'])
	
	# Initialize AuthHelper
	auth = AuthHelper(db)

# Convenience function for mako template lookup & rendering
# handles template lookup, global variables, and encoding automagically
def tmplr(name, *args, **kwargs):
	auth.deleteStaleSessions()
	kwdict = {'ROOT_URL': config['global']['ROOT_URL'], 'authenticated': auth.authenticated(), 'admin': auth.is_admin(), 'session': auth.getSession()}
	kwdict.update(kwargs)
	return lookup.get_template(name).render_unicode(**kwdict).encode('utf-8', 'replace')

# Dynamically handles errors - HTTP 404, 500, etc...
def handle_error(status, message, traceback, version):
	# This check allows the failsafe omission of trailing slashes on URLs
	if cherrypy.request.path_info[-1] == "/":
		# Redirect to the same URL without the trailing /
		cherrypy.response.headers['Location'] = cherrypy.request.path_info[0:-1]
		cherrypy.response.status = 301
	else:
		# TODO: Determine what kind of error!
		return str(tmplr("404.html", test1="<h2>404<h2>", test2="<br />File Not Found<br /><pre>%s</pre>" % str(traceback)))


class STEAM(object):
	
	# Homepage
	# /
	@cherrypy.expose
	def index(self):
		return tmplr("home.html")
	
	# Register Page
	# /register
	@cherrypy.expose
	def register_page(self, **kwargs):
		if cherrypy.request.method != 'POST':
			return tmplr("register.html")
		
		if not all(k in kwargs for k in ('email', 'username', 'password', 'confirm', 'first_name', 'last_name') or not all(kwargs[k] != "" for k in kwargs)):
			return tmplr("register.html", success=False, error_message="All fields are required", fields=kwargs)
		
		if kwargs['password'] != kwargs['confirm']:
			return tmplr("login.html", success=False, error_message="Passwords do not match", fields=kwargs)
		
		success = auth.register(kwargs['email'], kwargs['username'], kwargs['password'], kwargs['first_name'], kwargs['last_name'], kwargs['admin'])
		
		raise cherrypy.HTTPRedirect("/register", success=success, message="")
	
	# Login Page
	# /login
	@cherrypy.expose
	def login_page(self, **kwargs):
	
		if cherrypy.request.method != 'POST':
			if auth.authenticated():
				raise cherrypy.HTTPRedirect("/user/cpanel")
			else:
				return tmplr("login.html", success=True, error_message="", token="")
		
		if not all(k in kwargs for k in ('username', 'password') or not all(kwargs[k] != "" for k in kwargs)):
			return tmplr("login.html", success=False, error_message="All fields are required", fields=json.dumps(kwargs))
		
		success, error_message, token = auth.login(kwargs['username'], kwargs['password'])
		
		if not success:
			return tmplr("login.html", success=success, error_message=error_message, fields=json.dumps(kwargs))
		else:
			if auth.is_admin(token):
				return tmplr("admin_cpanel.html", initsession=token, admin=auth.is_admin(token), session=auth.getSession(token))
			else:
				return tmplr("cpanel_home.html", initsession=token, admin=auth.is_admin(token), session=auth.getSession(token))
		
	# Auth: Logout
	# /auth/logout
	@cherrypy.expose
	def auth_logout(self):
		auth.logout()
		
		try:
			cherrypy.response.cookie['steam_token'] = cherrypy.request.cookie['steam_token'].value
			cherrypy.response.cookie['steam_token']['expires'] = 0
		except:
			pass
		
		raise cherrypy.HTTPRedirect("/login")
	
	# Auth: Get Session
	# /auth/getsession
	@cherrypy.expose
	def auth_getsession(self):
		return json.dumps(auth.getSession())
	
	# Ajax: Javascript Error Logging
	# /ajax/jslog
	@cherrypy.expose
	def ajax_jslog(self, **kwargs):
		if cherrypy.request.method != 'POST':
			raise cherrypy.HTTPError(404)
		
		with open("%sjavascript_errors.log" % config['global']['log.js_file'], 'a+') as jslog:
			jslog.write("\n[%s] <%s><%s: Line %s> %s" % (timestamp(), kwargs['href'], kwargs['script'], kwargs['line'], kwargs['msg']))
		
		return json.dumps({'success': True})

class Admin(object):
	# For any admin views we have
	pass
