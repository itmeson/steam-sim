import Image

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
			return super(Result, self).__getattr__(name)

class ProfileManager(object):
	
	def __init__(self, db, auth, imagepath, imageurl):
		self.db = db
		self.auth = auth
		self.imagepath = imagepath
		self.imageurl = imageurl
		
		self.users = self.db.get_table('user_accounts')
		self.sessions = self.db.get_table('user_sessions')
		self.profiles = self.db.get_table('user_profiles')
		self.perms_problem = self.db.get_table('perms_problem')
		self.perms_problemset = self.db.get_table('perms_problemset')
		
		self.editable_attrs = {
			'first_name': {'table': self.users, 'column': 'first_name'},
			'last_name': {'table': self.users, 'column': 'last_name'},
			'image': {'table': self.profiles, 'column': 'image'},
			'science': {'table': self.profiles, 'column': 'interest_science'},
			'technology': {'table': self.profiles, 'column': 'interest_technology'},
			'engineering': {'table': self.profiles, 'column': 'interest_engineering'},
			'art': {'table': self.profiles, 'column': 'interest_art'},
			'math': {'table': self.profiles, 'column': 'interest_math'}
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
		return Result({'success': true,
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
		except:
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
	
	# Updates an existing user profile
	def updateProfile(self, user_id=None, token=None, **kwargs):
		user = self.getUser(user_id=user_id, token=token)
		
		if not user.success:
			return user
		
		if 'image' in kwargs:
			imagepath = self.saveImage(kwargs['image'])
			self.db.update(self.users, {'image': kwargs['image'].filename}, self.users.c.id == user.user_id)
			del kwargs['image']
		
		account_attrs = {k: v for k, v in kwargs.iteritems() if k in self.editable_attrs and self.editable_attrs[k]['table'] == self.users}
		profile_attrs = {k: v for k, v in kwargs.iteritems() if k in self.editable_attrs and self.editable_attrs[k]['table'] == self.profiles}
		
		self.db.update(self.users, account_attrs, self.users.c.id == user.user_id)
		self.db.update(self.profiles, profile_attrs, self.profiles.c.user_id == user.user_id)
		
	
	