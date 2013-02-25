from random import choice
import json

class SummationHandler:
	
	# Datasets
	datasets = [{'dataset': {'dataset': "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"}, 'answer': 55},
				{'dataset': {'dataset': "2, 4, 6, 8, 10"}, 'answer': 31},
				]
	
	def createInstanceData(self):
		return {'downloadable': True, 'data': choice(self.datasets)}
	
	def formatProblemDesc(self, desc, data):
		return desc.format(vars=data)
	
	def validateAnswer(self, data, uinput):
		data = json.loads(instance.data)
		return int(uinput) == instance.data['data']['answer']