"""Database and plots update scripts. 

This script fetches two datasets from the Fitbit API:
	activities: General data on running, walking and other activities. This is 
	collected from the last 10 days. 
	intraday_steps: Daily steps data (steps/15min) for the current day.  	

These are then stored as tables in the Dashboard database. Plots coming from 
these datasets are created, and stored in the /static/img/ folder. 

Methods: 
	* update_activities_table: Update table 'activities' in database.
	* update_steps_table: Update table 'steps_intraday' in database. 
	* main: Update all tables and plots.  
""" 
import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta 
from dashboard.server import Server 
from dashboard.fitbit_API import Fitbit 
from dashboard.make_plots import plot_activities, plot_steps
from sqlalchemy.types import Integer, Text, String, DateTime 

def update_activities_table(): 
	"""Fetch Fitbit activities data from API for the last 10 days. Update 
	activities table in Dashboard database. 
	""" 
	server = Server() 
	fb_config = server.get_fitbit_config() 
	fitbit = Fitbit(**fb_config) 

	# Get activities data from last 10 days 
	yesterday = datetime.today() - timedelta(days=1) 
	date_range = pd.date_range(end=yesterday, periods=10)  
	date_range = [date.strftime("%Y-%m-%d") for date in date_range] 

	df_list = [] 
	url = 'https://api.fitbit.com/1/user/-/activities/date/{}.json'  
	for date in date_range:
		response = fitbit.get_resource(url.format(date))  

		# Log unexpected responses 
		if response.status_code != 200:
			with open("./logs/errors.log", "a") as f: 
				msg = "Error getting activities for date: {}".format(date) 
				code = "Response status code: {}".format(response.status_code) 
				demarker = "------------------------------------" 
				f.write("{}\n{}\n{}\n".format(msg, code, demarker)) 

			continue 

		response = response.json() 

		if response['activities']: 
			df = pd.DataFrame(response['activities']) 

			# Adjust duration column from millisec to minutes 
			if 'duration' in df.columns: 
				df.duration = df.duration.apply(lambda x: round(x/60000)) 

			df = df.rename(columns={ 
				'startTime': 'start_time', 
				'startDate': 'date', 
				'duration': 'duration_min',
				'distance': 'distance_km'
				})  
		else: 
			# Treat missing data as walk with zero steps (inactive days) 
			df = pd.DataFrame(data={
				'name': 'Walk',
				'description': 'Inactive', 
				'steps': 0,
				'date': date 
				},  
				index=[0]
				)    

		wanted_columns = [ 
				'name', 'description', 'start_time', 'duration_min', 
				'steps', 'distance_km', 'calories', 'date' 
				]  

		# Record missing values as NaNs 
		for col in wanted_columns:
			if col not in df.columns: 
				df[col] = np.NaN 

		df = df[wanted_columns] 
		df_list.append(df) 

	total_df = pd.concat(df_list) 

	# Store dataframe as SQL table 
	engine = server.make_engine() 
	table_name = 'activities' 

	total_df.to_sql( 
			table_name, 
			engine, 
			if_exists='replace',
			index=False,
			chunksize=500,
			dtype={ 
				"name": Text,
				"description": Text,
				"start_time": Text, 
				"duration_min": Integer, 
				"steps": Integer,
				"distance": Text,
				"calories": Integer,
				"date": DateTime 
			}
			) 

def update_steps_table():	
	"""Fetch Fitbit intraday steps data from API for today, which consists 
	of stepcount returned for each 15min interval until now. Pad time between 
	now and midnight with zeros. Update steps_intraday table in Dashboard 
	database.  
	""" 
	# init Fitbit client 
	server = Server() 
	fb_config = server.get_fitbit_config() 
	fitbit = Fitbit(**fb_config) 

	url='https://api.fitbit.com/1/user/-/activities/steps/date/{}/1d/15min.json' 
	
	today = datetime.today().strftime("%Y-%m-%d") 
	response = fitbit.get_resource(url.format(today)) 

	# Log unexpected responses 
	if response.status_code != 200: 
		with open("./logs/errors.log", "a") as f: 
			msg = "Error getting activities for date: {}".format(date) 
			code = "Response status code: {}".format(response.status_code) 
			demarker = "------------------------------------" 
			f.write("{}\n{}\n{}\n".format(msg, code, demarker)) 

	response = response.json() 

	# Get the intraday steps data 
	response = response['activities-steps-intraday']['dataset']	
	df = pd.DataFrame(response)  
	
	# Convert the minute data to datetime 
	df.time = pd.to_datetime(df.time) 

	# Zero-fill the remaining 15-min datapoints from now to midnight 
	last_record = df.time.iloc[-1]  
	start = last_record + timedelta(minutes=15) 
	end = pd.to_datetime("23:59:59") 

	minutes_index = pd.date_range(start=start, end=end, freq="15min")

	zero_df = pd.DataFrame(0, index=minutes_index, columns=['value']) 
	zero_df['time'] = zero_df.index  

	df = df.append(zero_df) 

	# Store dataframe as SQL table 
	engine = server.make_engine() 
	table_name = 'steps_intraday' 

	df.to_sql(
			table_name, 
			engine, 
			if_exists='replace',
			index=False,
			chunksize=500,
			dtype={
				"time": DateTime,
				"value": Integer
			}
			) 

def main(): 
	"""Update activities and steps_intraday SQL tables. Refresh activities 
	and steps plots in /static/img folder. To be run on a schedule (e.g. via 
	crontab). 
	"""
	update_activities_table()
	update_steps_table()
	plot_activities()
	plot_steps() 

if __name__=="__main__": 
	main() 
