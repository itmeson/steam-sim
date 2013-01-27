from string import letters, digits
import random
import bcrypt
import json
import cherrypy

# Dictionary that allows for use of .attribute syntax
class Result(dict):
	def __init__(self, d=None):
		if d:
			for k, v in d.iteritems():
				self[k] = v
	
	def __getattr__(self, name):
		try:
			return self.__getitem__(name)
		except KeyError:
			return super(DictObj,self).__getattr__(name)

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
		self.cookiename = "steam_token"
		self.users = self.db.get_table('user_accounts')
		self._users = "user_accounts"
		self.sessions = self.db.get_table('user_sessions')
		self._sessions = "user_sessions"
		self.perms_problem = self.db.get_table('perms_problem')
		self.perms_problemset = self.db.get_table('perms_problemset')
	
	##
	# Util: Generate Token
	##
	def generateToken(self, length):
		return ''.join(random.choice(letters + digits) for x in range(length))
	
	##
	# Util: Get Token If Exists
	##
	def getTokenIfExists(self):
		return cherrypy.request.cookie[self.cookiename].value if self.cookiename in cherrypy.request.cookie else None
	
	##
	# Util: Create New Session
	##
	def createSession(self, id):
		self.db.delete(self.sessions, sessions.c.user_id == id);
		token = self.generateToken(12)
		self.db.insert(self.sessions, {'user_id': id, 'token': token})
		return token
	
	##
	# Util: Is User Authenticated?
	##
	@session
	def authenticated(self, token=None):
		if self.getSession(token)['success']:
			return True
		return False
	
	##
	# Util: Is User Admin?
	##
	@session
	def is_admin(self, token=None):
		if not token:
			token = self.getTokenIfExists()
		
		if not token:
			return False
		
		session = self.getSession(token)
		if not session['success']:
			return False
		
		users = self.db.select(self.users, self.users.c.id == session['user_id'])
		
		if not len(users):
			return False
		
		if not users[0].admin:
			return False
		return True
	
	##
	# Util: Is User Super Admin?
	##
	@session
	def is_superadmin(self, token=None):
		if not token:
			token = self.getTokenIfExists()
		
		if not token:
			return False
		
		session = self.getSession(token)
		if not session['success']:
			return False
		
		users = self.db.select(self.users, self.users.c.id == session['user_id'])
		
		if not len(users):
			return False
		
		if not users[0].superadmin:
			return False
		return True
	
	##
	# Auth: Delete stale sessions
	##
	def deleteStaleSessions(self):
		self.db.raw("DELETE FROM %s WHERE lastupdate < (NOW() - INTERVAL 10 MINUTE)" % self._sessions)
		return Result({'success': True})
	
	##
	# Auth: Update Session
	##
	def updateSession(self, token=None):
		if not token:
			token = self.getTokenIfExists()
		
		if not token:
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Token"})
		
		self.db.update(self.sessions, {'lastupdate': now()}, self.sessions.c.token == token)
		return Result({'success': True})
	
	##
	# Auth: Get Session
	##
	@session
	def getSession(self, token=None):
		if not token:
			token = self.getTokenIfExists()
		
		if not token:
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Token"})
		
		sessions = self.db.select(self.sessions, self.sessions.c.token == token)
		
		if not len(sessions):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Token"})
		
		users = self.db.select(self.users, self.users.c.id == sessions[0].user_id)
		
		if not len(users):
			return Result({'success': False, 'ecode': 1, 'message': "User does not exist"})
		
		return Result({'success': True, 'token': token, 'user_id': users[0].id, 'username': users[0].username, 'first_name': users[0].first_name, 'last_name': users[0].last_name, 'admin': users[0].admin, 'superadmin': users[0].superadmin})
		
	##
	# Auth: Logout
	##
	@session
	def logout(self, token=None):
		if not token:
			token = self.getTokenIfExists()
		
		if not token:
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Token"})
		
		self.db.delete(self.sessions, self.sessions.c.token == token)
		
		cherrypy.response.cookie[self.cookiename] = token
		cherrypy.response.cookie[self.cookiename]['expires'] = 0
			
		return Result({'success': True})
	
	##
	# Auth: Login
	##
	@session
	def login(self, username, password):
		
		users = self.db.select(self.users, self.users.c.username == username)
		if not len(users):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Username"})
		
		if(bcrypt.hashpw(password, users[0].password) != users[0].password):
			return Result({'success': False, 'ecode': 1, 'message': "Invalid Password"})
		
		token = self.createSession(users[0].id)
		
		return Result({'success': True, 'token': token})
		
	##
	# Register
	##
	@session
	def register(self, username, password, email, first_name, last_name, admin, superadmin):
		username = username.lower()
		users = self.db.select(self.users, self.users.c.username == username)
		if len(users):
			return Result({'success': False, 'ecode': 0, 'message': "Username already exists"})
		
		hashed = bcrypt.hashpw(password, bcrypt.gensalt())
		
		self.db.insert(self.users, {'username': username, 'password': hashed, 'email': email, 'first_name': first_name, 'last_name': last_name, 'admin': admin, 'superadmin': superadmin})
		users = self.db.select(self.users, self.users.c.username == username)
		return Result({'success': True})
		