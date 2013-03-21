from sqlalchemy import and_, or_
from utils import DictObj as Result
from utils import enum
from handlers import *

class ProblemManager(object):
	
	def __init__(self, db, auth, profile):
		self.db = db
		self.auth = auth
		self.profile = profile
		
		self.handlers = Result({
							"SummationHandler": SummationHandler(),
							"AdditionHandler": AdditionHandler(),
							"ConversionHandler": ConversionHandler()
						})
		
		self.type = enum(Science=1,
						Technology=2,
						Engineering=3,
						Art=4,
						Math=5
						)
		
		self.problems = self.db.get_table('problems')
		self.problemsets = self.db.get_table('problemsets')
		self.links = self.db.get_table('set_links')
		self.urls = self.db.get_table('problem_urls')
		self.instances = self.db.get_table('problem_instances')
	
	
	# ----------
	# - Get Handlers
	# ----------
	def getHandlers(self):
		return self.handlers.keys()
	
	# ----------
	# - Get Problem
	# ----------
	def getProblem(self, problem_id):
		problems = self.db.select(self.problems, self.problems.c.id == problem_id)
		if len(problems):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Problem ID"})
		
		urls = self.db.select(self.urls, self.urls.problem_id == problem_id)
		
		return Result({'success': True,
						'problem_id': problems[0].id,
						'type': problems[0].type,
						'name': problems[0].name,
						'slug': problems[0].slug,
						'desc': problems[0].desc,
						'creator': self.profile.getUser(user_id=problems[0].creator),
						'background': problems[0].background,
						'handler': problems[0].handler,
						'urls': [url.url for url in urls]
						})
	
	
	# ----------
	# - Get All Problems
	# ----------
	def getAllProblems(self):
		return [Result({'problem_id': problem.id,
					'type': problem.type,
					'name': problem.name,
					'slug': problem.slug,
					'desc': problem.desc,
					'creator': self.profile.getUser(user_id=problem.creator),
					'background': problem.background,
					'handler': problem.handler
					})
					for problem in self.db.select(self.problems)]
	
	
	# ----------
	# - Get Problem Instance
	# ----------
	def getProblemInstance(self, problem_id):
		instances = self.db.select(self.instances, self.instances.c.id == problem_id)
		if not len(instances):
			return Result({'success': False, 'ecode': 0, 'message': "Instance does not exist"})
		
		return Result({'success': True,
						'problem_id': instances[0].problem_id,
						'user_id': instances[0].user_id,
						'completed': instances[0].completed,
						'data': instances[0].data,
						'start': instances[0].start,
						'end': instances[0].end
						})
	
	
	# ----------
	# - Get Problem URLs
	# ----------
	def getProblemURLs(self, problem_id):
		urls = self.db.select(self.urls, self.urls.c.problem_id == problem_id)
		
		return {'success': True,
				'urls': [url.url for url in urls]}
	
	
	# ----------
	# - Get All Problem URLs
	# ----------
	def getAllProblemURLs(self):
		urls = self.db.select(self.urls)
		
		return [Result({'url_id': url.id,
					'problem_id': url.problem_id,
					'url': url.url})
				for url in urls]
	
	
	# ----------
	# - Get Problem Set
	# ----------
	def getProblemSet(self, set_id):
		sets = self.db.select(self.problemsets, self.problemsets.c.id == set_id)
		if not len(sets):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Set ID"})
		
		links = self.db.select(self.links, self.links.c.set_id == sets[0].id)
		
		problems = [self.db.select(self.problems, self.problems.c.id == link.problem_id)[0] for link in links]
		
		return Result({'success': True,
						'set_id': sets[0].id,
						'name': sets[0].name,
						'slug': sets[0].slug,
						'desc': sets[0].desc,
						'creator': self.profile.getUser(user_id=sets[0].creator),
						'problems': [Result({'problem_id': problem.id,
										'type': problem.type,
										'name': problem.name,
										'slug': problem.slug,
										'creator': self.profile.getUser(user_id=problem.creator)
									}) for problem in problems]
						})
	
	
	# ----------
	# - Get All Problem Sets
	# ----------
	def getAllProblemSets(self):
		sets = self.db.select(self.problemsets)
		
		return [Result({'success': True,
						'set_id': set.id,
						'name': set.name
						}) for set in sets]
	
	
	# ----------
	# - Get Set Link
	# ----------
	def getSetLink(self, set_id, problem_id):
		links = self.db.select(self.links, and_(self.links.c.set_id == set_id, self.links.c.problem_id == problem_id))
		
		if not len(links):
			return Result({'success': False, 'ecode': 0, 'message': "Set Link Does Not Exist"})
		
		return Result({'success': True, 'set_id': links[0].set_id, 'problem_id': links[0].problem_id})
	
	
	# ----------
	# - Get Set Links
	# ----------
	def getSetLinks(self, set_id):
		links = self.db.select(self.links, self.links.c.set_id == set_id)
		
		return Result({'success': True,
						'links': [
							{'link_id': link.id,
							'set_id': link.set_id,
							'problem_id': link.problem_id}
							for link in links]
						})
	
	
	# ----------
	# - Get All Set Links
	# ----------
	def getAllSetLinks(self):
		links = self.db.select(self.links)
		
		return [Result({'link_id': link.id,
				'set_id': link.set_id,
				'problem_id': link.problem_id})
				for link in links]
	
	
	# ----------
	# - Create Problem
	# ----------
	def createProblem(self, ptype, name, slug, desc, background, handler, creator, urls):
		problems = self.db.select(self.problems, or_(self.problems.c.name == name, self.problems.c.slug == slug))
		
		if len(problems):
			return Result({'success': False, 'ecode': 0, 'message': "Problem with that name already exits"})
		
		self.db.insert(self.problems, {'type': ptype, 'name': name, 'slug': slug, 'desc': desc, 'background': background, 'handler': handler, 'creator': creator})
		problems = self.db.select(self.problems, self.problems.c.name == name)
		for url in urls:
			self.createProblemURL(problems[0].id, url)
		return Result({'success': True})
	
	
	# ----------
	# - Create Problem Instance
	# ----------
	def createProblemInstance(self, problem_id):
		instance = self.getProblemInstance(problem_id)
		
		if instance.success:
			return Result({'success': False, 'ecode': 0, 'message': "Problem Instance already exists"})
		
		user = self.auth.getSession()
			
		self.db.insert(self.instances, {'problem_id': problem_id, 'user_id': user.user_id})
		return Result({'success': True})
	
	
	# ----------
	# - Create Problem URL
	# ----------
	def createProblemURL(self, problem_id, url):
		self.db.insert(self.urls, {'problem_id': problem_id, 'url': url})
		return Result({'success': True})
	
	
	# ----------
	# - Create Problem Set
	# ----------
	def createProblemSet(self, name, slug, desc):
		sets = self.db.select(self.problemsets, or_(self.problemsets.c.name == name, self.problemsets.c.slug == slug))
		
		if len(sets):
			return Result({'success': False, 'ecode': 0, 'message': "Problem set with that name already exits"})
		
		self.db.insert(self.problemsets, {'name': name, 'slug': slug, 'desc': desc})
		return Result({'success': True})
	
	
	# ----------
	# - Create Set Link
	# ----------
	def createSetLink(self, set_id, problem_id):
		links = self.db.select(self.links, and_(self.links.c.set_id == set_id, self.links.c.problem_id == problem_id))
		
		if len(links):
			return Result({'success': False, 'ecode': 0, 'message': "Problem set link already exists"})
		
		self.db.insert(self.links, {'set_id': set_id, 'problem_id': problem_id})
		return Result({'success': True})
	
	
	# ----------
	# - Delete Problem
	# ----------
	def deleteProblem(self, problem_id):
		self.db.delete(self.problems, self.problems.c.id == problem_id)
		self.db.delete(self.links, self.links.c.problem_id == problem_id)
		self.db.delete(self.urls, self.urls.c.problem_id == problem_id)
		return Result({'success': True})
	
	
	# ----------
	# - Delete Problem URL
	# ----------
	def deleteProblemURL(self, url_id):
		self.db.delete(self.urls, self.urls.c.id == url_id)
		return Result({'success': True})
	
	
	# ----------
	# - Delete All Problem URLs
	# ----------
	def deleteAllProblemURLs(self, problem_id):
		self.db.delete(self.urls, self.urls.c.problem_id == problem_id)
		return Result({'success': True})
	
	
	# ----------
	# - Delete Problem Instance
	# ----------
	def deleteProblemInstance(self, instance_id):
		self.db.delete(self.instances, self.instances.c.id == instance_id)
		return Result({'success': True})
	
	
	# ----------
	# - Delete Problem Set
	# ----------
	def deleteProblemSet(self, set_id):
		self.db.delete(self.problemsets, self.problemsets.c.id == set_id)
		self.db.delete(self.links, self.links.c.set_id == set_id)
		return Result({'success': True})
	
	
	# ----------
	# - Delete Set Link
	# ----------
	def deleteSetLink(self, link_id=None, set_id=None, problem_id=None):
		if link_id:
			self.db.delete(self.links, self.links.c.id == link_id)
		else:
			self.db.delete(self.links, and_(self.links.c.set_id == set_id, self.links.c.problem_id == problem_id))
	
	# ----------
	# - Delete All Set Links
	# ----------
	def deleteAllSetLinks(self, set_id=None, problem_id=None):
		if not set_id:
			self.db.delete(self.links, self.links.c.problem_id == problem_id)
		elif not problem_id:
			self.db.delete(self.links, self.links.c.set_id == set_id)
		return Result({'success': True})

