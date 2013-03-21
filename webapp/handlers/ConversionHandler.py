from random import choice
import json

class ConversionHandler:
	
	# Datasets
	datasets = [{'dataset': {'x': 12}, 'answer': 1},
				{'dataset': {'x': 36}, 'answer': 3}
				]
	
	def createInstanceData(self):
		return {'downloadable': False, 'data': choice(datasets)}
	
	def formatProblemDesc(self, desc, data):
		return desc.format(vars=data)
	
	def validateAnswer(self, instance, uinput):
		return int(uinput) == instance.data['data']['answer']
