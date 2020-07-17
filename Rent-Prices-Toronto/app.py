from flask import Flask, render_template, session, redirect, url_for 
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField 
from wtforms.validators import NumberRange

import numpy as np 
from scripts.predictions import predict_price 
import joblib 

app = Flask(__name__)
# Configure a secret SECRET_KEY
app.config['SECRET_KEY'] = 'your_secret_key'  

# Loading model and transformers 
model = joblib.load('./model/model.pkl')   
imp = joblib.load('./model/imp.pkl') 
onehot = joblib.load('./model/onehot.pkl') 

# Create a WTForm class 
class ApartmentFeaturesForm(FlaskForm): 
	bedrooms = TextField('Bedrooms') 
	bathrooms = TextField('Bathrooms')  
	sqft = TextField('Sqft') 
	city = TextField('City') 
	postal_code = TextField('Postal code') 
	longitude = TextField('Longitude') 
	latitude = TextField('Latitude') 
	submit = SubmitField('Predict price')  
	back = SubmitField('Back')

@app.route('/', methods=['GET', 'POST']) 
def index():
	# Create instance of the form.
	form = ApartmentFeaturesForm() 

	# If the form is valid on submission 
	if form.validate_on_submit(): 
		# Grab the data from the input on the form. 
		session['bedrooms'] = form.bedrooms.data
		session['bathrooms'] = form.bathrooms.data
		session['sqft'] = form.sqft.data
		session['city'] = form.city.data
		session['postal_code'] = form.postal_code.data
		session['longitude'] = form.longitude.data
		session['latitude'] = form.latitude.data 
		
		return redirect(url_for("prediction")) 

	return render_template('home.html', form=form)    

@app.route('/prediction', methods=['GET', 'POST'])  
def prediction():
	# Create instance of the form. 
	form = ApartmentFeaturesForm() 

	# Go back to index 
	if form.is_submitted(): 
		return redirect(url_for("index")) 

	# Some input sanitization on session values 
	for key in session: 
		if not session[key]:
			session[key] = np.NaN  

	# Define user_input dictionary 
	user_input = {
			'bedrooms': float(session['bedrooms']), 
			'bathrooms': float(session['bathrooms']),  
			'sqft': float(session['sqft']), 
			'city': str(session['city']), 
			'postal_code': str(session['postal_code']),  
			'longitude': float(session['longitude']), 
			'latitude': float(session['latitude'])  
			}  

	results = predict_price(model=model, imp=imp, onehot=onehot, 
							user_input=user_input)   
	return render_template('prediction.html', form=form, results=results)


if __name__ == '__main__':  
	app.run(debug=True) 
