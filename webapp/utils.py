from datetime import datetime
import pickle
import json
import yaml

def timestamp(dtobj=None):
	 if not dtobj:
	 	return datetime.strftime(datetime.now(), "%d/%m/%y %H:%M:%S")
	 else:
	 	return dtobj.strftime("%d/%m/%y %H:%M:%S")

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	enums['r'] = dict((value, key) for key, value in enums.iteritems())
	return type('Enum', (), enums)

class DictObj(dict):
	
	def __setattr__(self, key, value):
		self.__setitem__(key, value)
	
	def __getattr__(self, key):
		try:
			return self.__getitem__(key)
		except KeyError:
			raise AttributeError(key)
	
	def __delattr__(self, key):
		try:
			self.__delitem__(key)
		except KeyError:
			raise AttributeError(key)
	
	def serialize(self, method, indent=None, flow=None):
		if method == 'json':
			return json.dumps(dict(self), indent=indent)
		elif method == 'yaml':
			return yaml.dump(dict(self), default_flow_style=flow)
		elif method == 'pickle':
			return pickle.dumps(self)
	
	def json(self, **kwargs):
		return self.serialize('json', **kwargs)
	
	def yaml(self, **kwargs):
		return self.serialize('yaml', **kwargs)
	
	def pickle(self, **kwargs):
		return self.serialize('pickle', **kwargs)