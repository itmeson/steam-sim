from string import letters, digits
from sqlalchemy.sql.functions import now
import random
import bcrypt
import json
import cherrypy

def session(func):
	def wrapped(self, *args, **kwargs):
		self.deleteStaleSessions()
		rv = func(self, *args, **kwargs)
		self.updateSession()
		return rv
	return wrapped

class AuthHelper(object):
	
	def __init__(self, db):
		self.db = db
	
	# UTIL: Generate session token or App ID
	def generateToken(self, length):
		return ''.join(random.choice(letters + digits) for x in range(length))
	
	# UTIL: Delete old sessions
	def deleteStaleSessions(self):
		self.db.raw("DELETE FROM sessions WHERE lastupdate < (NOW() - INTERVAL 10 MINUTE)")
	
	# ACTION: Heartbeat
	def updateSession(self, token=None):
		if not token:
			if 'uvb_token' in cherrypy.request.cookie:
				token = cherrypy.request.cookie['uvb_token'].value
			else:
				return {'success': 0, 'ecode': 0}
		sessions = self.db.get_table('sessions')
		rows = self.db.update(sessions, {'lastupdate': now()}, sessions.c.token == token)
		return {'success': 1, 'message': "Session Updated"}
	
	# UTIL: Check if user is logged in
	@session
	def isLoggedIn(self, user_id):
		sessions = self.db.get_table('sessions')
		rows = self.db.select(sessions, sessions.c.user_id == user_id)
		if len(rows):
			return True
		return False
	
	# UTIL: Check if session is valid
	@session
	def sessionValid(self, token):
		sessions = self.db.get_table('sessions')
		rows = self.db.select(sessions, sessions.c.token == token)
		if len(rows):
			return True
		return False
	
	# ACTION: getsession
	@session
	def getSession(self, token=None):
		self.deleteStaleSessions()
		self.updateSession()
		
		if not token:
			if 'uvb_token' not in cherrypy.request.cookie:
				return {'success': 0, 'message': "Invalid Token"}
			token = cherrypy.request.cookie['uvb_token'].value
		
		sessions = self.db.get_table('sessions')
		rows = self.db.select(sessions, sessions.c.token == token)
		if not len(rows):
			return {'success': 0, 'message': "Invalid Token"}
		
		users = self.db.get_table('users')
		rows = self.db.select(users, users.c.id == rows[0].user_id)
		if not len(rows):
			return {'success': 0, 'message': "Invalid Token"}
		
		return {'success': 1, 'token': token, 'user_id': rows[0].id, 'username': rows[0].username, 'first_name': rows[0].first_name, 'last_name': rows[0].last_name, 'message': "Welcome, %s!" % rows[0].username}
	
	# UTIL: Create new session
	@session
	def createSession(self, id):
		sessions = self.db.get_table('sessions')
		self.db.raw("DELETE FROM sessions WHERE user_id = %s" % id)
		token = self.generateToken(12)
		
		self.db.insert(sessions, {'user_id': id, 'token': token})
		return token
	
	# ACTION: Logout
	@session
	def logout(self):
		sessions = self.db.get_table('sessions')
		self.db.raw("DELETE FROM sessions WHERE token = '%s'" % cherrypy.request.cookie['uvb_token'].value)
		return {'success': 1, 'message': "Logged Out"}
	
	# ACTION: Login
	@session
	def login(self, username, password):
		self.deleteStaleSessions()
		
		users = self.db.get_table('users')
		rows = self.db.select(users, users.c.username == username)
		if not len(rows):
			return False, "Invalid Username", False
		
		if(bcrypt.hashpw(password, rows[0].password) != rows[0].password):
			return False, "Invalid Password", False
		
		token = self.createSession(rows[0].id)
		
		return True, "", token
	
	# ACTION: Register
	@session
	def register(self, email, username, password, first_name, last_name, admin):
		username = username.lower()
		users = self.db.get_table('users')
		rows = self.db.select(users, users.c.username == username)
		if len(rows):
			return False
		
		hashed = bcrypt.hashpw(password, bcrypt.gensalt())
		self.db.insert(users, {'email': email, 'username': username, 'password': hashed, 'first_name': first_name, 'last_name': last_name, 'admin': admin})
		rows = self.db.select(users, users.c.username == username)
		token = self.createSession(rows[0].id)
		return True
	
	@session
	def get_session_by_token(self, token=None):
		if not token:
			if 'uvb_token' not in cherrypy.request.cookie:
				return None
			
			sessions = self.db.get_table('sessions')
			rows = self.db.select(sessions, sessions.c.token == cherrypy.request.cookie['uvb_token'].value)
			if len(rows) == 0:
				return None
			else:
				return rows[0]
		else:
			sessions = self.db.get_table('sessions')
			rows = self.db.select(sessions, sessions.c.token == token)
			if len(rows) == 0:
				return None
			else:
				return rows[0]
	
	@session
	def get_session_by_name(self, user):
		if 'uvb_token' not in cherrypy.request.cookie:
			return None
		
		users = self.db.get_table('users')
		rows = self.db.select(users, users.c.username == user)
		if len(rows) == 0:
			return None
		user = rows[0]
		
		sessions = self.db.get_table('sessions')
		rows = self.db.select(sessions, (sessions.c.token == cherrypy.request.cookie['uvb_token'].value) & (sessions.c.user_id == user.id))
		if len(rows) == 0:
			return None
		else:
			return rows[0]
	
	@session
	def logged_in(self, user=None):
		if user:
			if self.get_session_by_name(user):
				return True
		if self.get_session_by_token():
			return True
		return False
	
	@session
	def authenticated(self, users=None):
		if not users:
			if self.get_session_by_token():
				return True
			return False
		for user in users:
			if self.logged_in(user):
				return True
	
	@session
	def is_admin(self, token=None):
		if not token:
			session = self.get_session_by_token()
			if not session:
				return None
			users = self.db.get_table('users')
			rows = self.db.select(users, users.c.id == session.user_id)
			if len(rows) == 0:
				return None
			else:
				if rows[0].admin:
					return True
				else:
					return False
		else:
			session = self.get_session_by_token(token)
			if not session:
				return None
			users = self.db.get_table('users')
			rows = self.db.select(users, users.c.id == session.user_id)
			if len(rows) == 0:
				return None
			else:
				if rows[0].admin:
					return True
				else:
					return False