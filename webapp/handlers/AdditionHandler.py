from random import choice
import json

class AdditionHandler:
	
	# Datasets
	datasets = [{'dataset': {'x': 1, 'y': 2}, 'answer': 3},
				{'dataset': {'x': 100, 'y': 2}, 'answer': 102},
				{'dataset': {'x': 16, 'y': 24}, 'answer': 40},
				{'dataset': {'x': 18, 'y': 77}, 'answer': 95},
				{'dataset': {'x': 8, 'y': 11}, 'answer': 19},
				{'dataset': {'x': 1, 'y': 555}, 'answer': 556},
				]
	
	def createInstanceData(self):
		return {'downloadable': False, 'data': choice(datasets)}
	
	def formatProblemDesc(self, desc, data):
		return desc.format(vars=data)
	
	def validateAnswer(self, instance, uinput):
		return int(uinput) == instance.data['data']['answer']