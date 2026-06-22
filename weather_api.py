import requests
import random
from datetime import datetime

class WeatherAPI:
    def __init__(self):
        # You would put your actual API key here
        self.api_key = 'your_openweather_api_key'
        self.base_url = 'http://api.openweathermap.org/data/2.5'
    
    def get_current_weather(self, lat, lon):
        """Get current weather data from API"""
        try:
            # For demo purposes, return simulated data
            # In production, you would make actual API calls
            return self.simulate_current_weather(lat, lon)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self.get_fallback_weather()
    
    def simulate_current_weather(self, lat, lon):
        """Simulate current weather data for demonstration"""
        # Determine season based on current month
        month = datetime.now().month
        if month in [10, 11, 12]:  # Northeast monsoon
            rainfall = random.uniform(5, 25)
            wind_direction = random.choice(['NE', 'N', 'E'])
        elif month in [6, 7, 8, 9]:  # Southwest monsoon
            rainfall = random.uniform(2, 15)
            wind_direction = random.choice(['SW', 'W', 'S'])
        else:  # Summer
            rainfall = random.uniform(0, 5)
            wind_direction = random.choice(['SE', 'E', 'S'])
        
        return {
            'temperature': round(random.uniform(28, 36), 1),
            'humidity': round(random.uniform(65, 90), 1),
            'pressure': round(random.uniform(1005, 1015), 1),
            'wind_speed': round(random.uniform(10, 25), 1),
            'wind_direction': wind_direction,
            'rainfall': round(rainfall, 1)
        }
    
    def get_fallback_weather(self):
        """Return fallback weather data when API fails"""
        return {
            'temperature': 30.0,
            'humidity': 70.0,
            'pressure': 1010.0,
            'wind_speed': 15.0,
            'wind_direction': 'NE',
            'rainfall': 0.0
        }