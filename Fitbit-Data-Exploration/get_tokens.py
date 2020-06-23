"""     
Script to obtain access_token, refresh_token and expired_at from output of gather_keys_oauth2.py 
Writes to tokens.json  
Use once to authorise client 
""" 
import json  
import os

# load credentials
with open("./oauth/credentials.json", "r") as f:
	credentials = json.load(f)

client_id = credentials['client_id']
client_secret = credentials['client_secret']

# write script output to text file   
os.system("python3 ./oauth/gather_keys_oauth2.py %s %s >tokens.txt" % (client_id, client_secret))   
 
# extract access_token, refresh_token, expired_at from token file
with open("tokens.txt", "r") as f: 
	access_token = refresh_token = expires_at = None
	for line in f: 
		line_split = line.split('=')
		if len(line_split) != 2:  # skip lines not following 'key = value' scheme
			continue
		k, v = [x.strip() for x in line_split]
		if k == 'access_token':
			access_token = v
		elif k == 'refresh_token':
			refresh_token = v  
		elif k == 'expires_at':
			expires_at = v 

tokens = {}
tokens['access_token'] = access_token
tokens['refresh_token'] = refresh_token
tokens['expires_at'] = expires_at  

# store in json
with open("./oauth/tokens.json", "w") as f:
	json.dump(tokens, f)   

# clean up 
os.system("rm tokens.txt")  
