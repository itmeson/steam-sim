import Image

# image = Image.open("filename")
# image = image.resize((width, height), Image.ANTIALIAS)
# image.save("filename.ext", "EXT")

class ProfileManager(object):
	
	attrs = []
	
	def __init__(self, db, auth):
		self.db = db
		self.auth = auth
		
		self.users = self.db.get_table('user_accounts')
		self.profiles = self.db.get_table('user_profiles')
		self.perms_problem = self.db.get_table('perms_problem')
		self.perms_problemset = self.db.get_table('perms_problemset')
	
	def createProfile(self):
		pass
	
	def deleteProfile(self):
		pass
	
	def getProfile(self):
		pass
	
	def updateProfile(self, **kwargs):
		pass
	
	