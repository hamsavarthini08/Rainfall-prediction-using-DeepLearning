import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

class DataProcessor:
    def __init__(self):
        self.historical_data = None
        self.locations_data = None
        self.load_data()
    
    def load_data(self):
        """Load historical data and locations from CSV files"""
        try:
            # Load locations
            if os.path.exists('data/locations.csv'):
                self.locations_data = pd.read_csv('data/locations.csv')
                print(f"Loaded {len(self.locations_data)} locations from CSV")
            else:
                print("Locations CSV not found, using default data")
                self.create_default_locations()
            
            # Load historical weather data
            if os.path.exists('data/tamilnadu_weather.csv'):
                self.historical_data = pd.read_csv('data/tamilnadu_weather.csv')
                # Parse date
                self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
                print(f"Loaded {len(self.historical_data)} historical weather records")
            else:
                print("Weather data CSV not found, creating sample data")
                self.historical_data = self.create_sample_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.historical_data = self.create_sample_data()
            self.create_default_locations()
    
    def create_default_locations(self):
        """Create default locations data"""
        locations_data = {
            'name': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem'],
            'district': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem'],
            'latitude': [13.0827, 11.0168, 9.9252, 10.7905, 11.6643],
            'longitude': [80.2707, 76.9558, 78.1198, 78.7047, 78.1460],
            'coastal': ['Yes', 'No', 'No', 'No', 'No'],
            'elevation': [6, 411, 101, 88, 278]
        }
        self.locations_data = pd.DataFrame(locations_data)
    
    def get_location_coordinates(self, location_name):
        """Get coordinates for a location"""
        if self.locations_data is not None:
            location_data = self.locations_data[self.locations_data['name'] == location_name]
            if len(location_data) > 0:
                return {
                    'lat': float(location_data.iloc[0]['latitude']),
                    'lon': float(location_data.iloc[0]['longitude']),
                    'coastal': location_data.iloc[0]['coastal'],
                    'elevation': float(location_data.iloc[0]['elevation'])
                }
        
        # Default fallback
        return {'lat': 11.1271, 'lon': 78.6569, 'coastal': 'No', 'elevation': 100}
    
    def get_historical_data(self, location, date):
        """Get historical weather data for specific location and date"""
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # Filter data for location
            location_data = self.historical_data[
                self.historical_data['location'] == location
            ]
            
            if len(location_data) > 0:
                # Try exact date first
                exact_match = location_data[location_data['date'] == date_obj]
                
                if len(exact_match) > 0:
                    row = exact_match.iloc[0]
                else:
                    # Get data from same month and approximate day
                    month_data = location_data[
                        (location_data['date'].dt.month == date_obj.month) &
                        (location_data['date'].dt.day >= date_obj.day - 3) &
                        (location_data['date'].dt.day <= date_obj.day + 3)
                    ]
                    
                    if len(month_data) > 0:
                        row = month_data.iloc[0]
                    else:
                        # Get any data from same month
                        month_data = location_data[
                            location_data['date'].dt.month == date_obj.month
                        ]
                        if len(month_data) > 0:
                            row = month_data.iloc[0]
                        else:
                            return self.get_default_weather(location)
                
                return {
                    'temperature': float(row['temperature']),
                    'humidity': float(row['humidity']),
                    'pressure': float(row['pressure']),
                    'wind_speed': float(row['wind_speed']),
                    'wind_direction': row['wind_direction'],
                    'rainfall': float(row['rainfall']),
                    'cloud_cover': float(row.get('cloud_cover', 50)),
                    'evaporation': float(row.get('evaporation', 5))
                }
            else:
                return self.get_default_weather(location)
                
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return self.get_default_weather(location)
    
    def get_yearly_trends(self, location, year):
        """Get yearly weather trends for a location"""
        try:
            location_data = self.historical_data[
                (self.historical_data['location'] == location) &
                (self.historical_data['date'].dt.year == int(year))
            ].copy()
            
            if len(location_data) > 0:
                # Group by month
                monthly_trends = {}
                for month in range(1, 13):
                    month_data = location_data[location_data['date'].dt.month == month]
                    
                    if len(month_data) > 0:
                        monthly_trends[month] = {
                            'rainfall': float(month_data['rainfall'].mean()),
                            'temperature': float(month_data['temperature'].mean()),
                            'humidity': float(month_data['humidity'].mean()),
                            'wind_speed': float(month_data['wind_speed'].mean()),
                            'wind_direction': month_data['wind_direction'].mode().iloc[0] if len(month_data) > 0 else 'NE',
                            'pressure': float(month_data['pressure'].mean()),
                            'cloud_cover': float(month_data['cloud_cover'].mean()) if 'cloud_cover' in month_data.columns else 50,
                            'rainy_days': int((month_data['rainfall'] > 0).sum())
                        }
                    else:
                        monthly_trends[month] = {
                            'rainfall': 0,
                            'temperature': 30,
                            'humidity': 70,
                            'wind_speed': 15,
                            'wind_direction': 'NE',
                            'pressure': 1010,
                            'cloud_cover': 50,
                            'rainy_days': 0
                        }
                
                return monthly_trends
            else:
                return self.get_default_trends()
                
        except Exception as e:
            print(f"Error getting yearly trends: {e}")
            return self.get_default_trends()
    
    def get_all_locations(self):
        """Get list of all locations"""
        if self.locations_data is not None:
            return sorted(self.locations_data['name'].unique().tolist())
        else:
            return ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem', 
                    'Tirunelveli', 'Vellore', 'Erode', 'Thanjavur', 'Kanyakumari']
    
    def get_location_details(self, location_name):
        """Get detailed information about a location"""
        if self.locations_data is not None:
            location_data = self.locations_data[self.locations_data['name'] == location_name]
            if len(location_data) > 0:
                return location_data.iloc[0].to_dict()
        return None
    
    def get_default_weather(self, location):
        """Return default weather data if historical not found"""
        return {
            'temperature': 30.0,
            'humidity': 75.0,
            'pressure': 1010.0,
            'wind_speed': 15.0,
            'wind_direction': 'NE',
            'rainfall': 0.0,
            'cloud_cover': 50,
            'evaporation': 5.0
        }
    
    def get_default_trends(self):
        """Return default trends data"""
        trends = {}
        for month in range(1, 13):
            trends[month] = {
                'rainfall': 0,
                'temperature': 30,
                'humidity': 70,
                'wind_speed': 15,
                'wind_direction': 'NE',
                'pressure': 1010,
                'cloud_cover': 50,
                'rainy_days': 0
            }
        return trends