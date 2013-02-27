from string import letters, digits
from sqlalchemy.sql.functions import now
import random
import bcrypt
import json
import cherrypy

from utils import DictObj as Result

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
		self.vtokens = self.db.get_table('verification_tokens')
	
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
		self.db.delete(self.sessions, self.sessions.c.user_id == id);
		token = self.generateToken(12)
		self.db.insert(self.sessions, {'user_id': id, 'token': token})
		return token
	
	##
	# Util: Create Verification Token (for verification emails)
	##
	def createVerificationToken(self, id):
		vtoken = self.generateToken(48)
		self.db.insert(self.vtokens, {'user_id': id, 'token': vtoken})
		return vtoken
	
	##
	# Util: Check to see if Verification Token exists
	##
	def vtokenValid(self, vtoken):
		vtokens = self.db.select(self.vtokens, self.vtokens.c.token == vtoken)
		if not len(vtokens):
			return False
		return True
	
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
		self.db.raw("DELETE FROM %s WHERE lastupdate < (NOW() - INTERVAL 1 HOUR)" % self._sessions)
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
		
		if not users[0].active:
			return Result({'success': False, 'ecode': 2, 'message': "This user account is deactivated"})
		
		return Result({'success': True, 'token': token, 'user_id': users[0].id, 'username': users[0].username, 'first_name': users[0].first_name, 'last_name': users[0].last_name, 'active': users[0].active, 'admin': users[0].admin, 'superadmin': users[0].superadmin})
	
	##
	# Auth: Login Page
	##
	@session
	def login(self, username, password, ignoreactive=False):
		
		users = self.db.select(self.users, self.users.c.username == username)
		if not len(users):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Username"})
		
		if not ignoreactive:
			if not users[0].active:
				return Result({'success': False, 'ecode': 1, 'message': "This user account is deactivated"})
		
		if bcrypt.hashpw(password, users[0].password) != users[0].password:
			return Result({'success': False, 'ecode': 2, 'message': "Invalid Password"})
		
		return Result({'success': True, 'token': self.createSession(users[0].id)})
		
	##
	# Auth: Register
	##
	@session
	def register(self, username, password, email, first_name, last_name, admin, superadmin):
		username = username.lower()
		users = self.db.select(self.users, self.users.c.username == username)
		if len(users):
			return Result({'success': False, 'ecode': 0, 'message': "Username already exists"})
		
		users = self.db.select(self.users, self.users.c.email == email)
		if len(users):
			return Result({'success': False, 'ecode': 0, 'message': "The provided email has already been used for registration"})
		
		hashed = bcrypt.hashpw(password, bcrypt.gensalt())
		
		self.db.insert(self.users, {'username': username, 'password': hashed, 'email': email, 'first_name': first_name, 'last_name': last_name, 'admin': admin, 'superadmin': superadmin})
		users = self.db.select(self.users, self.users.c.username == username)
		
		vtoken = self.createVerificationToken(users[0].id)
		
		return Result({'success': True, 'vtoken': vtoken, 'user_id': users[0].id, 'first_name': users[0].first_name, 'last_name': users[0].last_name, 'email': users[0].email})
	
	##
	# Auth: Activate
	##
	@session
	def activate(self, vtoken):
		vtokens = self.db.select(self.vtokens, self.vtokens.c.token == vtoken)
		if not len(vtokens):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Verification Token"})
		
		users = self.db.select(self.users, self.users.c.id == vtokens[0].user_id)
		if not len(users):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Verification Token"})
		
		self.db.update(self.users, {'active': True}, self.users.c.id == users[0].id)
		
		self.db.delete(self.vtokens, self.vtokens.c.token == vtoken)
		
		return Result({'success': True, 'user_id': users[0].id})
		
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
		