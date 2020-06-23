"""A class Server to handles communicating with the Dashboard MySQL database. 
""" 
import pandas as pd 
import pymysql 
from sqlalchemy import create_engine 

class Server: 
	"""A class that handles communicating with the Dashboard database. 

	Attributes: 
	db_config: A database configuration dictionary.	 
	""" 

	db_config = { 
			'db_type': 'mysql', 
			'con': 'pymysql', 
			'host': 'localhost',
			'usr': 'username', 
			'pw': 'password', 
			'db': 'Dashboard', 
			}

	def __init__(self): 
		pass 

	def make_engine(self):  
		"""Create an sqlalchemy engine to connect to Dashboard database. 
		
		:return: An sqlalchemy engine 
		:rtype: <class 'sqlalchemy.engine.base.Engine'> 
		"""
		s = "{db_type}+{con}://{usr}:{pw}@{host}/{db}".format(**self.db_config) 
		return create_engine(s) 

	def get_fitbit_config(self): 
		"""Fetch the Fitbit config from the database. This config is necessary 
		to talk to the Fitbit API.  

		:return: A dictionary with five keys: 
				client_id: Your Fitbit app client id 
				:type client_id: str
				client_secret: Your Fitbit app client secret 
				:type client_secret: str
				access_token: An oauth2 access token 
				:type access_token: str 
				refresh_token: The corresponding refresh token 
				:type refresh_token: str
				expires_at: The unix time at which access_token expires 
				(e.g. 1591749405.1234567) 
				:type expires_at: str 
		:rtype: dict   
		""" 
		# Connect to MySQL database 
		engine = self.make_engine()
		db = engine.connect() 

		# Build query 
		query = "SELECT {} FROM credentials WHERE id = 1" 
		columns = [
				'client_id',
				'client_secret',
				'access_token',
				'refresh_token',
				'expires_at'
				] 

		columns = ", ".join(columns) 
		query = query.format(columns) 

		# Read credentials table into dict 
		df = pd.read_sql(query, db) 
		db.close()  

		fb_config = df.to_dict(orient='records')[0] 
		fb_config.update({'token_update_method': self.update_fitbit_tokens}) 

		return fb_config 

	def update_fitbit_tokens(self, token_dict): 
		"""Updates token data in database. This is for when access_token expires
		and new tokens are fetched. 

		:param token_dict: The token dictionary (json file) sent from Fitbit 
		servers in response to a token refresh request. 
		:type token_dict: dict 
		""" 
		engine = self.make_engine() 

		# Prepare SQL query 
		# UPDATE table SET col1=val1, col2=val2, ... WHERE condition 
		query = "UPDATE credentials SET {} WHERE id = 1" 

		data = ["{}=\'{}\'".format(key, token_dict[key]) for key in token_dict] 
		data = ', '.join(data) 

		query = query.format(data) 

		# Run UPDATE query 
		engine.execute(query) 
