"""A Class Fitbit which handles all requests interactions with the Fitbit WEB 
API. see https://dev.fitbit.com/build/reference/web-api/ for details. 
""" 
import json  
import requests 
import time 

class Fitbit: 
	"""A simple class for calling the Fitbit WEB API via oauth2, 
	see https://dev.fitbit.com/build/reference/web-api/ for details. 

	Handles the oauth2 token refresh process automatically. 
   
	:param client_id: Your Fitbit app client id
	:type client_id: str
	:param client_secret: Your Fitbit app client secret 
	:type client_secret: str
	:param access_token: An oauth2 access token 
	:type access_token: str
	:param refresh_token: The corresponding refresh token
	:type refresh_token: str
	:param expires_at: The unix time at which access_token expires 
	(e.g. 1591749405.1234567) 
	:type expires_at: str 
	:param token_update_method: A method accepting a token dict for refreshing
	tokens in static storage (e.g. a database), used to refresh tokens as they 
	expire  
	:type token_update_method: method 
	"""  

	def __init__(self, client_id=None, client_secret=None, 
				 access_token=None, refresh_token=None, 
				 expires_at=None, token_update_method=None):       

		self.client_id = client_id  
		self.client_secret = client_secret 
		self.access_token = access_token 
		self.refresh_token = refresh_token 
		self.expires_at = expires_at  
		self.token_update_method = token_update_method 

	def refresh_tokens(self): 
		"""Fetch a new token dictionary from Fitbit API, and refresh the token
		attributes (access_token, refresh_token, expires_at). Use the instance's
		token update method to refresh the static tokens.  
		""" 
		# Get new token dict from Fitbit server 
		response = requests.post(url='https://api.fitbit.com/oauth2/token', 
								 data={
									 "client_id": self.client_id, 
									 "grant_type": "refresh_token",
									 "refresh_token": self.refresh_token  
								 }, 
								 auth=(self.client_id, self.client_secret))   

		if response.status_code != 200:
			raise Exception('API response: {}'.format(response.status_code)) 

		tokens = response.json()  

		# Add the "expires_at" key-value pair 
		expires_in = float(tokens['expires_in']) 
		tokens['expires_at'] = time.time() + expires_in 

		# Update tokens in Fitbit instance 
		self.access_token = tokens['access_token']
		self.refresh_token = tokens['refresh_token'] 
		self.expires_at = tokens['expires_at'] 
			
		# Update static tokens file 
		if self.token_update_method: 
			self.token_update_method(tokens)  

	def get_resource(self, resource_url): 
		"""Wrapper for requests.get method, passing along access token. First 
		checks if access token has expired, and refresh it if necessary. 

		:params resource_url: URL for the resource API endpoint. 
		:type resource_url: str  
		:return: Response object.  
		:rtype: requests.Response 
		""" 
		# Check access token is still valid 
		if (not self.expires_at) or (time.time() >= float(self.expires_at)): 
			self.refresh_tokens() 

		# Make GET request 
		headers = {'Authorization': 'Bearer {}'.format(self.access_token)} 
		return requests.request('GET', url=resource_url, headers=headers)	
