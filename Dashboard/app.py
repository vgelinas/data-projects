"""Flask app to produce dashboard. """   
from flask import Flask, render_template  
from dashboard.make_plots import plot_activities, plot_steps 
app = Flask(__name__)

# Disable caching 
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/') 
def index(): 
	return render_template('index.html') 


if __name__=="__main__": 
	app.run(debug=True) 
