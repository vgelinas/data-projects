import pandas as pd 
from dashboard.server import Server 
from main import update_activities_table 

def test_update_activities_table(): 
	update_activities_table() 

	server = Server() 
	engine = server.make_engine()  
		
	df = pd.read_sql_table(
			table_name='activities',
			con=engine,	 
			parse_dates=['date']
		)   

	# Check all columns are there and contain valid entries 
	columns = ['name', 'description', 'start_time', 'duration_min', 
			   'steps', 'distance_km', 'calories', 'date'] 

	for col in columns:
		assert(col in df.columns) 
		assert(df[col].notna().any())  
