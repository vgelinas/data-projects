from dashboard.server import Server 

def test_get_fitbit_config(): 
	server = Server()
	Fitbit_config = server.get_fitbit_config() 
	assert(Fitbit_config != None)  

