import Image
from StringIO import StringIO

from utils import DictObj as Result

class ProfileManager(object):
	
	def __init__(self, db, auth, imagepath, imageurl):
		self.db = db
		self.auth = auth
		self.imagepath = imagepath
		self.imageurl = imageurl
		
		self.users = self.db.get_table('user_accounts')
		self.sessions = self.db.get_table('user_sessions')
		self.profiles = self.db.get_table('user_profiles')
		
		self.editable_attrs = {
			'first_name': {'table': 'users', 'column': 'first_name'},
			'last_name': {'table': 'users', 'column': 'last_name'},
			'image': {'table': 'profiles', 'column': 'image'},
			'science': {'table': 'profiles', 'column': 'interest_science'},
			'technology': {'table': 'profiles', 'column': 'interest_technology'},
			'engineering': {'table': 'profiles', 'column': 'interest_engineering'},
			'art': {'table': 'profiles', 'column': 'interest_art'},
			'math': {'table': 'profiles', 'column': 'interest_math'}
		}
	
	# Util: Get User Account
	def getUser(self, user_id=None, token=None):
		
		if not user_id:
			sessions = self.db.select(self.sessions, self.sessions.c.token == token)
			if not len(sessions):
				return Result({'success': False, 'ecode': 1, 'message': "Session does not exist"})
			
			users = self.db.select(self.users, self.users.c.id == sessons[0].user_id)
			if not len(users):
				return Result({'success': False, 'ecode': 0, 'message': "User does not exist"})
			user_id = users[0].id

		users = self.db.select(self.users, self.users.c.id == user_id)
		if not len(users):
			return Result({'success': False, 'ecode': 0, 'message': "User does not exist"})
		return Result({'success': True,
						'user_id': users[0].id,
						'username': users[0].username,
						'email': users[0].email,
						'first_name': users[0].first_name,
						'last_name': users[0].last_name,
						'active': users[0].active,
						'admin': users[0].admin,
						'superadmin': users[0].superadmin
						})		
	
	# Util: Get User Profile
	def getProfile(self, user_id=None, token=None):
		if not user_id:
			sessions = self.db.select(self.sessions, self.sessions.c.token == token)
			if not len(sessions):
				return Result({'success': False, 'ecode': 1, 'message': "Session does not exist"})
			
			users = self.db.select(self.users, self.users.c.id == sessons[0].user_id)
			if not len(users):
				return Result({'success': False, 'ecode': 0, 'message': "User does not exist"})
			user_id = users[0].id

		profiles = self.db.select(self.profiles, self.profiles.c.user_id == user_id)
		if not len(profiles):
			return Result({'success': False, 'ecode': 0, 'message': "User does not exist"})
		return Result({'success': True,
						'profile_id': profiles[0].id,
						'user_id': profiles[0].user_id,
						'joined': profiles[0].joined,
						'image': profiles[0].image,
						'science': profiles[0].interest_science,
						'technology': profiles[0].interest_technology,
						'engineering': profiles[0].interest_engineering,
						'art': profiles[0].interest_art,
						'math': profiles[0].interest_math
						})		
	
	# Util: Save Profile Image
	def saveImage(self, image, user_id=None, token=None):
		user = self.getUser(user_id=user_id, token=token)
		
		if not user.success:
			return user
		
		try:
			image = Image.open(image.file)
			image = image.resize((100, 100), Image.ANTIALIAS)
			image.save("%s%s.png" % (self.imagepath, user.username), "png")
			return Result({'success': True})
		except Exception:
			return Result({'success': False, 'ecode': 2, 'message': "Error opening image file"})
		
	# Creates a new user profile
	def createProfile(self, user_id, image, science, technology, engineering, art, math):
		users = self.db.select(self.users, self.users.c.id == user_id)
		
		if not len(users):
			return Result({'success': False, 'ecode': 0, 'message': "User does not exist"})
		
		if type(image) != str:
			result = self.saveImage(image)
			image = "%s%s.png" % (self.imageurl, users[0].username)
			if not result.success:
				return result
		
		self.db.insert(self.profiles, {'user_id': user_id, 'image': image, 'interest_science': science, 'interest_technology': technology, 'interest_engineering': engineering, 'interest_art': art, 'interest_math': math})
		
		profiles = self.db.select(self.profiles, self.profiles.c.user_id == user_id)
		
		self.db.update(self.users, {'profile_id': profiles[0].id}, self.users.c.id == user_id)
		
		return Result({'success': True})
	
	# Deletes an existing user account + profile
	def deleteUser(self, user_id=None, token=None):
		if not user_id:
			user_id = self.getUser(token=token).user_id
		
		self.db.delete(self.users, self.users.c.id == user_id)
		self.db.delete(self.profiles, self.profiles.c.user_id == user_id)
		
		return Result({'success': True})
	
	# Updates the profile image
	def updateImage(self, attrs):
		user = self.getUser(user_id=attrs['pk'])
		if not user.success:
			return user
		
		result = self.saveImage(attrs['image'], user_id=user.user_id)
		
		if not result.success:
			return result
		
		self.db.update(self.profiles, {'image': "%s%s.png" % (self.imageurl, user.username)}, self.profiles.c.user_id == user.user_id)
		return Result({'success': True})
	
	# Updates an existing user profile
	def updateProfile(self, attrs):
		user = self.getUser(user_id=attrs['pk'])
		
		if not user.success:
			return user
		
		if attrs['name'] in self.editable_attrs:
			if self.editable_attrs[attrs['name']]['table'] == "users":
				self.db.update(self.users, {self.editable_attrs[attrs['name']]['column']: attrs['value']}, self.users.c.id == user.user_id)
			elif self.editable_attrs[attrs['name']]['table'] == "profiles":
				self.db.update(self.profiles, {self.editable_attrs[attrs['name']]['column']: attrs['value']}, self.profiles.c.id == user.user_id)
		
		return Result({'success': True})
		
	
	