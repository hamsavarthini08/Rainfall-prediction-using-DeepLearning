import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from datetime import datetime

class FeatureEngineer:
    def __init__(self):
        self.wind_encoder = LabelEncoder()
        self.wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                               'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        self.wind_encoder.fit(self.wind_directions)
    
    def create_features(self, df):
        """Create additional features for model training"""
        df = df.copy()
        
        # Time-based features
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Cyclical encoding for time features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        # Wind direction encoding
        df['wind_direction_encoded'] = self.wind_encoder.transform(df['wind_direction'])
        df['wind_direction_sin'] = np.sin(2 * np.pi * df['wind_direction_encoded'] / 16)
        df['wind_direction_cos'] = np.cos(2 * np.pi * df['wind_direction_encoded'] / 16)
        
        # Interaction features
        df['temp_humidity'] = df['temperature'] * df['humidity'] / 100
        df['pressure_temp'] = df['pressure'] * df['temperature']
        df['wind_power'] = df['wind_speed'] * np.cos(2 * np.pi * df['wind_direction_encoded'] / 16)
        
        # Seasonal features
        df['season'] = df['month'].apply(self.get_season)
        
        # Rolling averages (if sequential data)
        if len(df) > 7:
            df['rainfall_rolling_7'] = df['rainfall'].rolling(window=7, min_periods=1).mean()
            df['temp_rolling_7'] = df['temperature'].rolling(window=7, min_periods=1).mean()
        
        return df
    
    def get_season(self, month):
        """Get season based on month"""
        if month in [3, 4, 5]:
            return 0  # Summer
        elif month in [6, 7, 8, 9]:
            return 1  # Southwest Monsoon
        elif month in [10, 11, 12]:
            return 2  # Northeast Monsoon
        else:
            return 3  # Winter
    
    def prepare_features_for_prediction(self, weather_data, sequence_length=30):
        """Prepare features for real-time prediction"""
        features = []
        
        # Extract features from weather data
        feature_columns = ['temperature', 'humidity', 'pressure', 'wind_speed', 
                          'wind_direction_encoded', 'latitude', 'longitude', 
                          'month', 'day', 'day_of_year', 'month_sin', 'month_cos',
                          'day_sin', 'day_cos', 'wind_direction_sin', 'wind_direction_cos']
        
        for data in weather_data[-sequence_length:]:
            row = []
            for col in feature_columns:
                if col in data:
                    row.append(data[col])
                else:
                    row.append(0)
            features.append(row)
        
        return np.array(features)
    
    def get_feature_importance(self, model, feature_names):
        """Get feature importance (for tree-based models)"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            return sorted(zip(feature_names, importance), key=lambda x: x[1], reverse=True)
        return None