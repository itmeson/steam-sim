from sqlalchemy import *

class Database(object):
	def __init__(self, host, user, pwd, database):
		self.connection_string = "mysql://%s:%s@%s/%s" % (user, pwd, host, database)
		self.db = create_engine(self.connection_string, pool_recycle=7200)
		self.metadata = MetaData(self.db)
	
	def get_table(self, table):
		return Table(table, self.metadata, autoload=True)
	
	def select(self, table, *args, **kwargs):
		if type(table) == str:
			table = self.get_table(table)
		c = select([table], *args, **kwargs)
		return c.execute().fetchall()
	
	def insert(self, table, values, *args, **kwargs):
		if type(table) == str:
			table = self.get_table(table)
		c = table.insert(values=values, *args, **kwargs)
		return c.execute()
	
	def update(self, table, values, *args, **kwargs):
		if type(table) == str:
			table = self.get_table(table)
		c = table.update(values=values, *args, **kwargs)
		return c.execute()
	
	def delete(self, table, *args, **kwargs):
		if type(table) == str:
			table = self.get_table(table)
		c = table.delete(*args, **kwargs)
		return c.execute()
	
	def raw(self, sql):
		conn = self.db.connect()
		result = conn.execute(sql)
		conn.close()
		return result
