"""Scripts to produce plots from the various tables in the Dashboard database.

This file contains two methods: 
	* plot_activities: Create a horizontal barplot of distances (km) for both
	the 'Walking' and 'Running' activities in the last 10 days. 
	* plot_steps: Create a barplot of steps/15min for the current day. 
""" 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import io  
from dashboard.server import Server  
plt.style.use('seaborn-dark') 

def plot_activities(): 
	"""Create horizontal barplot of activities distances (km) for Walking and 
	Running. Store as activities.png in /static/img/. 

	The distances are estimated from stepcount by using estimates for stride
	length, via the formula "distance = steps x stride length". The conversion
	factors are:

	0.0007366 km/step (walking)
	0.0011565 km/step (running) 
	"""  
	# Import activities table as dataframe	 
	server = Server()
	engine = server.make_engine() 
		
	df = pd.read_sql_table(
			table_name='activities',
			con=engine,	 
			parse_dates=['date']
		)   
	
	# Create columns for walking and running distance, 
	# converting steps to km using stride length estimates  
	walk_conversion = 0.0007366 
	run_conversion = 0.0011565 

	df['walking'] = df.steps.apply(lambda x: round(x * walk_conversion, 2))
	df['running'] = df.steps.apply(lambda x: round(x * run_conversion, 2)) 

	df.walking = df.walking.where(df.name == "Walk", 0)
	df.running = df.running.where(df.name == "Run", 0) 

	# Group together different activitity instances per day 
	df = df.groupby('date').sum() 
	df = df[['walking', 'running']] 

	# Use short names for dates, e.g. "Thu 11" 
	df.index = df.index.map(lambda x: x.strftime("%a %d")) 

	# Reverse dataframe to make horizontal barplot more pleasant 
	df = df.iloc[::-1] 

	# Horizontal barplot 
	fig, ax = plt.subplots() 
	df.plot(kind='barh') 
	plt.xlabel('Distance (km)') 
	plt.ylabel('') 
	plt.title('Recent activities') 

	# Save figure to static folder 
	plt.savefig("./static/img/activities.png") 
	
def plot_steps(): 
	"""Create barplot of stepcount data (steps/15min) for the current day. Plot
	is stored as steps.png in /static/img/.
	""" 
	# Import steps_intraday table as dataframe	  
	server = Server()
	engine = server.make_engine() 
		
	df = pd.read_sql_table(
			table_name='steps_intraday',
			con=engine,	 
			parse_dates=['time'] 
		)   

	df.rename(columns={'value': 'general activity'}, inplace=True)  
	df.set_index('time', inplace=True) 

	# Restrict to waking hours, e.g. after 6:00am 
	df = df.iloc[28:] 
					
	# Use short name for time 
	df.index = df.index.map(lambda x: x.strftime("%H:%M")) 

	# Barplot 
	fig, ax = plt.subplots() 
	ax = df.plot(kind='bar', rot=0, colormap='autumn')    

	# Barplots show ticks at every datapoint. 
	# Show only every 8th tick for readability. 
	every_nth = 8 
	for n, label in enumerate(ax.xaxis.get_ticklabels()): 
		if n % every_nth != 0: 
			label.set_visible(False) 

	# Hide the bottom 0 label on the y axis. 
	for n, label in enumerate(ax.yaxis.get_ticklabels()): 
		if n == 0:  
			label.set_visible(False) 

	ax.set_title('Hourly activity (steps)') 
	ax.set_xlabel('Time of day') 
	ax.set_ylabel('Steps / 15min') 
	
	# Save figure to static folder 
	plt.savefig("./static/img/steps.png") 
