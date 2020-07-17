import numpy as np
import pandas as pd 
import joblib 
import json 

def transform_user_input(imp, onehot, user_input):  
	"""Prepare user input for prediction using Imputer and OneHotEncoder 
	transformers.   

	Args: 
		imp (IterativeImputer instance): Fitted imputer to fill missing values.
		onehot (OneHotEncoder instance): Fitted encoder for categorical values.  
		user_input (dict): User supplied feature-value pairs.  

	Returns: 
		transformed_input (dataframe): A dataframe of shape (1, 129). 
	""" 
	# Turn input into dataframe 
	columns = ['bedrooms', 'bathrooms', 'sqft', 'latitude',
			   'longitude', 'city', 'postal_code'] 
	df = pd.DataFrame(user_input, columns=columns, index=[0]) 

    # Split into numerical and categorical columns 
	df_numerical = df[columns[:5]] 
	df_categorical = df[columns[5:7]] 
    
    # Impute missing values in the numerical columns 
	df_impute = pd.DataFrame(imp.transform(df_numerical), 
                             columns=df_numerical.columns)
    
    # Onehot encode categorical values
	df_onehot = pd.DataFrame(onehot.transform(df_categorical).toarray(), 
                             columns=onehot.get_feature_names())

    # Return merged dataframe
	return pd.merge(df_impute, df_onehot, left_index=True, right_index=True)

def predict_price(model, imp, onehot, user_input):    
	"""Predict monthly price based on user-supplied features. 
	
	Args: 
		model (XGBoost instance): Fitted model to make predictions. 
		imp (IterativeImputer instance): Fitted imputer to fill missing values.
		onehot (OneHotEncoder instance): Fitted encoder for categorical values. 
		user_input (dict): User supplied feature-value pairs.  

	Returns: 
		prediction (float): Predicted price.  
	""" 
	transformed_input = transform_user_input(imp, onehot, user_input)  
	print(model.predict(transformed_input)[0])
	return model.predict(transformed_input)[0] 
