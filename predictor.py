import numpy as np
import random
import hashlib
from datetime import datetime, timedelta
from utils.model_loader import ModelLoader
import pandas as pd

class RainfallPredictor:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.use_simulation = not self.model_loader.is_model_available()
        if self.use_simulation:
            print("Running in simulation mode - no trained model found")

    def _seed_from_inputs(self, lat, lon, date_str, context):
        """Create a stable seed so same location+date gives same prediction."""
        seed_key = f"{lat:.4f}|{lon:.4f}|{date_str}|{context}"
        digest = hashlib.sha256(seed_key.encode('utf-8')).hexdigest()
        return int(digest[:16], 16)

    def _get_rng(self, lat, lon, date_input, context):
        if isinstance(date_input, datetime):
            date_str = date_input.strftime('%Y-%m-%d')
        else:
            date_str = str(date_input)
        return random.Random(self._seed_from_inputs(lat, lon, date_str, context))
    
    def prepare_sequence(self, lat, lon, date, days_before=30):
        """Prepare sequence data for prediction"""
        # This would fetch historical data for the sequence
        # For now, generate synthetic sequence
        sequence = []
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
        for i in range(days_before):
            past_date = date_obj - timedelta(days=days_before - i)
            weather = self.simulate_weather_for_date(past_date, lat, lon)
            
            # Encode wind direction
            wind_directions = {'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
                              'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
                              'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
                              'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5}
            
            features = [
                weather['temperature'],
                weather['humidity'],
                weather['pressure'],
                weather['wind_speed'],
                wind_directions.get(weather['wind_direction'], 0),
                lat,
                lon,
                past_date.month,
                past_date.day
            ]
            sequence.append(features)
        
        return np.array(sequence)
    
    def predict_future_weather(self, lat, lon, date):
        """Predict future weather using trained model or simulation"""
        rng = self._get_rng(lat, lon, date, 'future_weather')
        
        # Try using deep learning model first
        if not self.use_simulation:
            sequence = self.prepare_sequence(lat, lon, date)
            
            # Try LSTM prediction
            rainfall = self.model_loader.predict_with_lstm(sequence)
            
            # If LSTM fails, try CNN-LSTM
            if rainfall is None:
                rainfall = self.model_loader.predict_with_cnn_lstm(sequence)
            
            # If both fail, fall back to simulation
            if rainfall is not None:
                # Generate other weather parameters
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                month = date_obj.month
                
                # Determine wind direction based on season
                if month in [10, 11, 12]:
                    wind_direction = rng.choice(['NE', 'N', 'E'])
                    wind_speed = rng.uniform(15, 25)
                elif month in [6, 7, 8, 9]:
                    wind_direction = rng.choice(['SW', 'W', 'S'])
                    wind_speed = rng.uniform(20, 30)
                else:
                    wind_direction = rng.choice(['SE', 'E', 'S'])
                    wind_speed = rng.uniform(10, 20)
                
                return {
                    'temperature': round(rng.uniform(27, 34), 1),
                    'humidity': round(rng.uniform(60, 85), 1),
                    'pressure': round(rng.uniform(1008, 1012), 1),
                    'wind_speed': round(wind_speed, 1),
                    'wind_direction': wind_direction,
                    'rainfall': round(max(rainfall, 0), 1)
                }
        
        # Fall back to simulation
        return self.simulate_future_weather(lat, lon, date)
    
    def simulate_weather_for_date(self, date, lat, lon):
        """Simulate weather for a specific date"""
        rng = self._get_rng(lat, lon, date, 'historical_sequence')
        month = date.month
        
        # Determine if coastal (simplified)
        coastal = lon > 79.5  # Rough approximation
        
        if month in [10, 11, 12]:  # Northeast monsoon
            rainfall = rng.uniform(10, 50)
            wind_direction = rng.choice(['NE', 'N', 'E'])
            wind_speed = rng.uniform(15, 30)
            temp = rng.uniform(26, 30)
            humidity = rng.uniform(75, 90)
        elif month in [6, 7, 8, 9]:  # Southwest monsoon
            rainfall = rng.uniform(5, 30)
            wind_direction = rng.choice(['SW', 'W', 'S'])
            wind_speed = rng.uniform(20, 35)
            temp = rng.uniform(28, 32)
            humidity = rng.uniform(70, 85)
        else:  # Summer/Winter
            rainfall = rng.uniform(0, 10)
            wind_direction = rng.choice(['SE', 'E', 'S'])
            wind_speed = rng.uniform(5, 20)
            temp = rng.uniform(30, 36) if month in [3,4,5] else rng.uniform(24, 28)
            humidity = rng.uniform(50, 70) if month in [3,4,5] else rng.uniform(60, 75)
        
        # Coastal adjustment
        if coastal:
            rainfall *= 1.3
            temp -= 2
            humidity += 5
        
        return {
            'temperature': round(temp, 1),
            'humidity': round(min(humidity, 100), 1),
            'pressure': round(rng.uniform(1005, 1015), 1),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': wind_direction,
            'rainfall': round(rainfall, 1)
        }
    
    def simulate_future_weather(self, lat, lon, date):
        """Simulate future weather data"""
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        rng = self._get_rng(lat, lon, date, 'future_simulation')
        month = date_obj.month
        
        if month in [10, 11, 12]:  # Northeast monsoon
            rainfall = rng.uniform(10, 40)
            wind_direction = rng.choice(['NE', 'N', 'E'])
            wind_speed = rng.uniform(15, 25)
            temp = rng.uniform(27, 31)
            humidity = rng.uniform(75, 85)
        elif month in [6, 7, 8, 9]:  # Southwest monsoon
            rainfall = rng.uniform(5, 25)
            wind_direction = rng.choice(['SW', 'W', 'S'])
            wind_speed = rng.uniform(20, 30)
            temp = rng.uniform(28, 32)
            humidity = rng.uniform(70, 80)
        else:  # Summer/Winter
            rainfall = rng.uniform(0, 8)
            wind_direction = rng.choice(['SE', 'E', 'S'])
            wind_speed = rng.uniform(10, 20)
            temp = rng.uniform(30, 35) if month in [3,4,5] else rng.uniform(25, 29)
            humidity = rng.uniform(55, 70) if month in [3,4,5] else rng.uniform(60, 70)
        
        return {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'pressure': round(rng.uniform(1008, 1012), 1),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': wind_direction,
            'rainfall': round(rainfall, 1)
        }
    
    def predict_weekly_forecast(self, lat, lon, days):
        """Predict weather for next N days"""
        predictions = []
        base_date = datetime.now().date()
        
        for i in range(days):
            future_date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            prediction = self.predict_future_weather(lat, lon, future_date)
            prediction['date'] = future_date
            predictions.append(prediction)
        
        return predictions
