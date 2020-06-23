from dashboard.fitbit_API import * 
from dashboard.server import * 
import requests 

def test_refresh_tokens(): 	
	# Instantiate fitbit client and refresh tokens 
	server = Server()
	fb_config = server.get_fitbit_config() 
	fitbit = Fitbit(**fb_config) 

	access_token = fb_config['access_token']
	refresh_token = fb_config['refresh_token'] 
	expires_at = fb_config['expires_at'] 

	fitbit.refresh_tokens()  # this refreshes both instance and static tokens 
	
	assert(access_token != fitbit.access_token) 
	assert(refresh_token != fitbit.refresh_token) 
	assert(expires_at != fitbit.expires_at) 

	# Check if token attributes are valid 
	response = requests.post( 
			url='https://api.fitbit.com/1.1/oauth2/introspect', 
		    data={
		   	    "client_id": fitbit.client_id, 
			    "grant_type": "Bearer {}".format(fitbit.access_token),
			    "token": fitbit.access_token   
		    }, 
		    auth=(fitbit.client_id, fitbit.client_secret))   

	assert(response.json()['active'] == True) 

	# Check if updated database tokens are also valid 
	fb_config2 = server.get_fitbit_config() 
	fitbit2 = Fitbit(**fb_config2) 

	response2 = requests.post(
			url='https://api.fitbit.com/1.1/oauth2/introspect', 
		    data={
			    "client_id": fitbit2.client_id, 
			    "grant_type": "Bearer {}".format(fitbit2.access_token),
			    "token": fitbit2.access_token   
		    }, 
		    auth=(fitbit2.client_id, fitbit2.client_secret))   

	assert(response2.json()['active'] == True) 

def test_get_resource(): 
	server = Server()
	fb_config = server.get_fitbit_config() 
	fitbit = Fitbit(**fb_config) 

	url = 'https://api.fitbit.com/1/user/-/activities/date/2020-05-01.json' 
	response = fitbit.get_resource(url) 
	assert(response.status_code == 200) 
