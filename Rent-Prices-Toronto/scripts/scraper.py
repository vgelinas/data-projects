#!/usr/bin/env python3 
from datetime import datetime 
import pandas as pd 
import numpy as np 

import contextlib 
import json
from lxml import html 
from ratelimit import limits, sleep_and_retry 
import re 
import requests 


@sleep_and_retry 
@limits(calls=1, period=5)  
def make_get_request(url): 
	"""Wrapper for get request, rated limited at 1 call/5sec.""" 
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'} 
	return requests.get(url, headers=headers) 

def build_rental_datasets(num_pages=1):   
	""" 
	Scrape rentals.ca/toronto and store properties info  
	as csv file in /data/ folder. 

	Columns extracted: 
		- price 
		- street address
		- city
		- postal code 
		- longitude 
		- latitude
		- rental type  
		- bedrooms
		- bathrooms 
		- sqft  
		- year built 
		- parking spots 
		- description_text 
	"""  
	# Each page contains a list of 10 rental ads, each with a url link to
	# their own page with further info. We scrape info from both pages. 
	pages = range(1, num_pages+1) 
	base_url = "https://rentals.ca/toronto?types=condo&types=apartment&types=house&beds=1%2B&sort=updated&p={}"

	rows = [] 
	for page in pages: 
		# Get response from page 
		url = base_url.format(page)  
		response = make_get_request(url) 
		tree = html.fromstring(response.content) 

		# Print progress bar 
		progress_bar(page=page, num_pages=num_pages, url=url) 

		# Log request 
		time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
		code = response.status_code 
		with open("../logs/requests.log", "a") as f: 
			message = "Time: {} | Code: {} | url: {}\n" 
			f.write(message.format(time, code, url))  

		# Log errors 
		if response.status_code != 200: 
			with open("../logs/requests_errors.log", "a") as f: 
				message = "Time: {} | Code : {} | url: {}\n"
				f.write(message.format(time, code, url))   
			
			continue 

		# Extract each json bit potentially associated to a rental ad 
		ads = tree.xpath('//script[@type="application/ld+json"]/text()') 
		ads_text = [str(element).strip().replace('\n', '') for element in ads] 
		data = [json.loads(json_text) for json_text in ads_text]  

		# Throw out json data not associated to a rental ad 
		data = [dct for dct in data if 'url' in dct] 

		for dct in data: 
			features = {}  

			# First we extract features from ad listed on the main page 
			with contextlib.suppress(KeyError):  
				features['street_address'] = dct['name'] 
				features['city'] = dct['containedInPlace']['name'] 
				features['postal_code'] = dct['address']['postalCode'] 
				features['price'] = dct['containsPlace'][0]['potentialAction']['priceSpecification']['price'] 
				features['longitude'] = dct['geo']['longitude'] 
				features['latitude'] = dct['geo']['latitude']  
				features['rental_type'] = dct['containsPlace'][0]['@type'] 
			
			# Then we follow the url and extract features from the ad's page 
			response = make_get_request(dct['url'])  

			# Log request 
			time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
			code = response.status_code 
			with open("../logs/requests.log", "a") as f: 
				message = "Time: {} | Code: {} | url: {}\n"
				f.write(message.format(time, code, dct['url']))  

			# Print progress bar when fetching new url 
			progress_bar(page=page, num_pages=num_pages, url=dct['url']) 

			# Parse content 
			tree = html.fromstring(response.content) 
			text = tree.xpath('//script[@type="text/javascript"]/text()') 
			text = text[1].replace('\n', '').strip() 

			# We extract features via regular expressions 
			regex = {
				'bedrooms': '"beds": ([0-9]\.0)', 
				'bathrooms': '"baths": ([0-9]\.0)', 
				'sqft': '"dimensions": ([0-9]*\.0)', 
				'description_text': '"description_text": "(.*)", "description_blurb"', 
				'year_built': '"answer": ([0-9]+), "answer_label": "Year Built"', 
				'parking_spots': '"answer": "(.+)", "answer_label": "Parking Spots"'
				} 

			with contextlib.suppress(AttributeError, IndexError): 
				for pattern in regex: 
					features[pattern] = re.search(regex[pattern], text).group(1)  

			rows.append(features) 

	# Store dataset 
	df = pd.DataFrame(rows)	 
	df.to_csv("../data/toronto_apartment_rentals_2020.csv", index=False)  

def progress_bar(page, num_pages, url): 
	"""
	Print a little progress bar to make waiting 10+ hours more pleasant. E.g.

	Looking at: https://www.rentals.ca/stuff       [                    ] 0% 
	Looking at: https://www.rentals.ca/stuff       [##########          ] 50% 
	Looking at: https://www.rentals.ca/stuff       [####################] 100%  
	""" 
	pct = "{:.0f}%".format(100*page/num_pages)  
	num_bars = round(20*page/num_pages) 
	bars = '[{}{}]'.format('#'*num_bars, ' '*(20-num_bars)) 
	msg = "Looking at: {}".format(url) 
	space = ' '*(143 - len(msg))

	progress_bar = ' '.join([msg, space, bars, pct]) 
	print(progress_bar)  


if __name__=="__main__":
	# Total pages: 684 
	# 684 * 11 requests at 1 request/5 secs: ~10.45 hours to build full dataset 
	build_rental_datasets(684)    
