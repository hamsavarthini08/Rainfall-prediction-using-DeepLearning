from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from utils.data_processor import DataProcessor
from utils.weather_api import WeatherAPI
from utils.predictor import RainfallPredictor

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize components
data_processor = DataProcessor()
weather_api = WeatherAPI()
predictor = RainfallPredictor()

# Load Tamilnadu locations
with open('data/locations.json', 'r') as f:
    locations = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', locations=locations)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', locations=locations)

@app.route('/get_weather_data', methods=['POST'])
def get_weather_data():
    try:
        data = request.json
        location = data['location']
        date = data['date']
        
        # Get coordinates for location
        coords = locations[location]
        
        # Get past data from dataset
        past_data = data_processor.get_historical_data(location, date)
        
        # Get present data from API
        present_data = weather_api.get_current_weather(coords['lat'], coords['lon'])
        
        # Get future predictions
        future_data = predictor.predict_future_weather(coords['lat'], coords['lon'], date)
        
        response = {
            'success': True,
            'past': past_data,
            'present': present_data,
            'future': future_data
        }
        
    except Exception as e:
        response = {
            'success': False,
            'error': str(e)
        }
    
    return jsonify(response)

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    try:
        data = request.json
        location = data['location']
        days = int(data['days'])
        
        coords = locations[location]
        predictions = predictor.predict_weekly_forecast(coords['lat'], coords['lon'], days)
        
        return jsonify({'success': True, 'predictions': predictions})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_historical_trends', methods=['POST'])
def get_historical_trends():
    try:
        data = request.json
        location = data['location']
        year = int(data['year'])
        
        trends = data_processor.get_yearly_trends(location, year)
        return jsonify({'success': True, 'trends': trends})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)