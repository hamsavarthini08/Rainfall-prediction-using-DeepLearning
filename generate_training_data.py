import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

class TrainingDataGenerator:
    def __init__(self):
        self.locations = {
            'Chennai': {'lat': 13.0827, 'lon': 80.2707, 'coastal': True},
            'Coimbatore': {'lat': 11.0168, 'lon': 76.9558, 'coastal': False},
            'Madurai': {'lat': 9.9252, 'lon': 78.1198, 'coastal': False},
            'Trichy': {'lat': 10.7905, 'lon': 78.7047, 'coastal': False},
            'Salem': {'lat': 11.6643, 'lon': 78.1460, 'coastal': False},
            'Tirunelveli': {'lat': 8.7139, 'lon': 77.7567, 'coastal': True},
            'Vellore': {'lat': 12.9165, 'lon': 79.1325, 'coastal': False},
            'Erode': {'lat': 11.3410, 'lon': 77.7172, 'coastal': False},
            'Thanjavur': {'lat': 10.7870, 'lon': 79.1378, 'coastal': True},
            'Kanyakumari': {'lat': 8.0883, 'lon': 77.5385, 'coastal': True},
            'Virudhunagar': {'lat': 9.5680, 'lon': 77.9624, 'coastal': False},
            'Dindigul': {'lat': 10.3624, 'lon': 77.9695, 'coastal': False},
            'Cuddalore': {'lat': 11.7446, 'lon': 79.7685, 'coastal': True},
            'Kanchipuram': {'lat': 12.8342, 'lon': 79.7038, 'coastal': True},
            'Namakkal': {'lat': 11.2210, 'lon': 78.1674, 'coastal': False}
        }
        
    def generate_historical_data(self, start_year=2010, end_year=2023):
        """Generate realistic historical weather data for Tamilnadu"""
        data = []
        
        for location, info in self.locations.items():
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    # Generate daily data for each month
                    days_in_month = 30 if month in [4, 6, 9, 11] else 31
                    if month == 2:
                        days_in_month = 29 if year % 4 == 0 else 28
                    
                    for day in range(1, days_in_month + 1, 3):  # Every 3 days to reduce data size
                        date = datetime(year, month, day)
                        
                        # Generate realistic weather patterns
                        weather_data = self.generate_weather_for_date(date, info)
                        weather_data['location'] = location
                        weather_data['date'] = date.strftime('%Y-%m-%d')
                        weather_data['latitude'] = info['lat']
                        weather_data['longitude'] = info['lon']
                        
                        data.append(weather_data)
        
        return pd.DataFrame(data)
    
    def generate_weather_for_date(self, date, location_info):
        """Generate realistic weather data based on season and location"""
        month = date.month
        
        # Temperature based on season
        if month in [3, 4, 5]:  # Summer
            base_temp = random.uniform(32, 38)
            humidity = random.uniform(50, 70)
        elif month in [6, 7, 8, 9]:  # Southwest Monsoon
            base_temp = random.uniform(28, 32)
            humidity = random.uniform(75, 90)
        elif month in [10, 11, 12]:  # Northeast Monsoon
            base_temp = random.uniform(26, 30)
            humidity = random.uniform(80, 95)
        else:  # Winter
            base_temp = random.uniform(24, 28)
            humidity = random.uniform(60, 75)
        
        # Adjust for coastal areas
        if location_info['coastal']:
            base_temp -= random.uniform(1, 2)
            humidity += random.uniform(5, 10)
        
        # Rainfall based on monsoon patterns
        rainfall = 0
        if month in [10, 11, 12]:  # Northeast Monsoon
            rainfall = random.uniform(10, 60)
            wind_direction = random.choice(['NE', 'N', 'E', 'NNE', 'ENE'])
            wind_speed = random.uniform(15, 30)
        elif month in [6, 7, 8, 9]:  # Southwest Monsoon
            rainfall = random.uniform(5, 35)
            wind_direction = random.choice(['SW', 'W', 'S', 'WSW', 'SSW'])
            wind_speed = random.uniform(20, 35)
        elif month in [1, 2]:  # Winter
            rainfall = random.uniform(0, 5)
            wind_direction = random.choice(['N', 'NE', 'E'])
            wind_speed = random.uniform(5, 15)
        else:  # Summer
            rainfall = random.uniform(0, 8)
            wind_direction = random.choice(['SE', 'S', 'E', 'ESE'])
            wind_speed = random.uniform(10, 20)
        
        # Coastal areas get more rainfall
        if location_info['coastal']:
            rainfall *= random.uniform(1.2, 1.5)
        
        # Pressure
        pressure = random.uniform(1005, 1015)
        if rainfall > 20:
            pressure -= random.uniform(2, 5)
        
        return {
            'temperature': round(base_temp + random.uniform(-2, 2), 1),
            'humidity': round(min(humidity + random.uniform(-5, 5), 100), 1),
            'pressure': round(pressure, 1),
            'wind_speed': round(wind_speed + random.uniform(-3, 3), 1),
            'wind_direction': wind_direction,
            'rainfall': round(max(rainfall + random.uniform(-2, 2), 0), 1)
        }

if __name__ == "__main__":
    generator = TrainingDataGenerator()
    df = generator.generate_historical_data(2010, 2023)
    df.to_csv('data/tamilnadu_weather.csv', index=False)
    print(f"Generated {len(df)} records of historical weather data")
    print(f"Data saved to data/tamilnadu_weather.csv")