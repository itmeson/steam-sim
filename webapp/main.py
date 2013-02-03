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
	kwdict = {'ROOT_URL': config['global']['ROOT_URL'], 'authenticated': auth.authenticated(), 'admin': auth.is_admin(), 'superadmin': auth.is_superadmin(), 'session': auth.getSession()}
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
	
	# Problems Page
	# /problems
	@cherrypy.expose
	def problems(self):
		return tmplr("problems.html")
	
	# Register Page
	# /register
	@cherrypy.expose
	def register_page(self, **kwargs):
		if cherrypy.request.method != 'POST':
			return tmplr("register.html", success=True, message="")
		
		if not all(k in kwargs for k in ('first_name', 'last_name', 'username', 'password', 'password_confirm', 'email', 'email_confirm') or not all(kwargs[k] != "" for k in kwargs)):
			del kwargs['password']
			del kwargs['password_confirm']
			return tmplr("register.html", success=False, message="All fields are required", fields=json.dumps(kwargs))
		
		if kwargs['password'] != kwargs['password_confirm']:
			del kwargs['password']
			del kwargs['password_confirm']
			return tmplr("register.html", success=False, message="Passwords do not match", fields=json.dumps(kwargs))
		
		if kwargs['email'] != kwargs['email_confirm']:
			del kwargs['password']
			del kwargs['password_confirm']
			return tmplr("register.html", success=False, message="Emails do not match", fields=json.dumps(kwargs))
		
		result = auth.register(kwargs['username'], kwargs['password'], kwargs['email'], kwargs['first_name'], kwargs['last_name'], False, False)
		
		if not result.success:
			return tmplr("register.html", success=False, message=result.message, fields=json.dumps(kwargs))
		
		emailer.send("STEAM Club", "%s %s" % (result.first_name, result.last_name), "steam@wilhall.com", result.email, "Activate Your Account", "Visit the following link to activate your account: http://steam.wilhall.com/auth/activate/%s" % result.vtoken)
		
		return tmplr("register.html", success=True, message="Thank you for registering! We will be sending you a confirmation email shortly.")
	
	# Login Page
	# /login
	@cherrypy.expose
	def login_page(self, **kwargs):
	
		if cherrypy.request.method != 'POST':
			if auth.authenticated():
				raise cherrypy.HTTPRedirect("/user/account")
			else:
				return tmplr("login.html", success=True, message="")
		
		if not all(k in kwargs for k in ('username', 'password') or not all(kwargs[k] != "" for k in kwargs)):
			return tmplr("login.html", success=False, message="All fields are required", fields=json.dumps({'username': kwargs['username']}))
		
		result = auth.login(kwargs['username'], kwargs['password'])
		
		if not result.success:
			return tmplr("login.html", success=False, message=result.message, fields=json.dumps({'username': kwargs['username']}))
		else:
			return tmplr("user_account.html", initsession=result.token, authenticated=auth.authenticated(result.token), admin=auth.is_admin(result.token), superadmin=auth.is_superadmin(result.token), session=auth.getSession(result.token))
	
	# Activate Page
	# /auth/activate
	@cherrypy.expose
	def auth_activate(self, **kwargs):
		
		if 'vtoken' not in kwargs:
			raise cherrypy.HTTPRedirect("/login")
		
		if not auth.vtokenValid(kwargs['vtoken']):
			raise cherrypy.HTTPRedirect("/login")
		
		if cherrypy.request.method != 'POST':
			if auth.authenticated():
				raise cherrypy.HTTPRedirect("/user/account")
			else:
				return tmplr("auth_activate.html", vtoken=kwargs['vtoken'], success=True, message="")
				
		
		if not all(k in kwargs for k in ('username', 'password') or not all(kwargs[k] != "" for k in kwargs)):
			return tmplr("auth_activate.html", vtoken=kwargs['vtoken'], success=False, message="All fields are required", fields=json.dumps({'username': kwargs['username']}))
		
		lresult = auth.login(kwargs['username'], kwargs['password'], ignoreactive=True)
		if not lresult.success:
			return tmplr("auth_activate.html", vtoken=kwargs['vtoken'], success=False, message=lresult.message, fields=json.dumps({'username': kwargs['username']}))
		
		aresult = auth.activate(kwargs['vtoken'])
		if not aresult.success:
			return tmplr("auth_activate.html", vtoken=kwargs['vtoken'], success=False, message=kresult.message, fields=json.dumps({'username': kwargs['username']}))
			
		return tmplr("user_account.html", initsession=lresult.token, admin=auth.is_admin(lresult.token), superadmin=auth.is_superadmin(lresult.token), session=auth.getSession(lresult.token))
	
	# Auth: Logout
	# /auth/logout
	@cherrypy.expose
	def auth_logout(self):
		
		auth.logout()
		
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

class Account(object):
	# User Account Page
	# /user/account
	@cherrypy.expose
	def user_account(self):
		if not auth.authenticated():
			raise cherrypy.HTTPRedirect("/login")
		
		return tmplr("user_account.html")
		
	
	# Ajax Edit Profile
	# /ajax/editprofile
	@cherrypy.expose
	def edit_profile(self, **kwargs):
		if cherrypy.request.method != 'POST':
			raise cherrypy.HTTPError(404)
		return json.dumps({'success': True, 'message': "Yep, it worked!"})

class Admin(object):
	# For any admin views we have
	pass
