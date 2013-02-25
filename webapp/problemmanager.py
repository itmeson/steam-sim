from utils import DictObj as Result
from utils import enum
import handlers

class ProblemManager(object):
	
	def __init__(self, db, auth, profile):
		self.db = db
		self.auth = auth
		self.profile = profile
		
		self.handler = Result({
							"SummationHandler": handlers.SummationHandler(),
							"AdditionHandler": handlers.AdditionHandler()
						})
		
		self.type = enum("Science",
						"Technology",
						"Engineering",
						"Art",
						"Math"
						)
		
		self.problems = self.db.get_table('problems')
		self.problemsets = self.db.get_table('problemsets')
		self.links = self.db.get_table('set_links')
		self.urls = self.db.get_table('problem_urls')
		self.instances = self.db.get_table('problem_instances')
	
	def getHandler(self, instance):
		return getattr(handler, self.handler.r[instance.handler])(instance)
	
	def createProblem(self, ptype, name, desc, background, handler, urls):
		self.db.insert(self.problems, {'type': ptype, 'name': name, 'desc': desc, 'background': background, 'handler': handler})
		problem = self.db.select(self.problems, self.problems.c.name == name)
		for url in urls:
			self.db.insert(self.urls, {'problem_id': problem.id, 'url': url})
		return Result({'success': True})
	
	def createProblemSet(self, name, desc):
		self.db.insert(self.problemsets, {'name': name, 'desc': desc})
		return Result({'success': True})
	
	def createProblemInstance(self, problem_id):
		instance = self.getProblemInstance(problem_id)
		
		if instance.success:
			return Result({'success': False, 'ecode': 0, 'message': "Problem Instance already exists"})
		
		user = self.auth.getSession()
			
		self.db.insert(self.instances, {'problem_id': problem_id, 'user_id': user.user_id})
		return Result({'success': True})
	
	def getProblem(self, problem_id):
		problems = self.db.select(self.problems, self.problems.c.id == problem_id)
		if len(problems):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Problem ID"})
		
		urls = self.db.select(self.urls, self.urls.problem_id == problem_id)
		
		return Result({'success': True,
						'problem_id': problems[0].id,
						'type': problems[0].type,
						'name': problems[0].name,
						'desc': problems[0].desc,
						'creator': self.profile.getUser(user_id=problems[0].creator),
						'background': problems[0].background,
						'handler': problems[0].handler,
						'urls': [url.url for url in urls]
						})
	
	def getProblemSet(self, set_id):
		sets = self.db.select(self.problemsets, self.problemsets.c.id == set_id)
		if len(sets):
			return Result({'success': False, 'ecode': 0, 'message': "Invalid Set ID"})
		
		links = self.db.select(self.links, self.links.c.set_id == sets[0].id)
		
		problems = [self.db.select(self.problems, self.problems.c.id == link.problem_id)[0] for link in links]
		
		return Result({'success': True,
						'set_id': sets[0].id,
						'name': sets[0].name,
						'desc': sets[0].desc,
						'creator': self.profile.getUser(user_id=sets[0].creator),
						'problems': [{'problem_id': problem.id,
										'type': problem.type,
										'name': problem.name,
										'desc': problem.desc,
										'creator': self.profile.getUser(user_id=problem.creator),
										'background': problem.background,
										'handler': problem.handler
									} for problem in problems]
						})
	
	def getProblemInstance(self, problem_id):
		instances = self.db.select(self.instances, self.instances.c.id == problem_id)
		if not len(instances):
			return Result({'success': False, 'ecode': 0, 'message': "Instance does not exist"})
		
		return Result({'success': True,
						'problem_id': instances[0].problem_id,
						'user_id': instances[0].user_id,
						'completed': instances[0].completed,
						'start': instances[0].start,
						'end': instances[0].end
						})