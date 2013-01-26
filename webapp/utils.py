from datetime import datetime

def timestamp(dtobj=None):
	 if not dtobj:
	 	return datetime.strftime(datetime.now(), "%d/%m/%y %H:%M:%S")
	 else:
	 	return dtobj.strftime("%d/%m/%y %H:%M:%S")