import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_tamilnadu_weather_data():
    """Generate realistic weather data for Tamilnadu locations"""
    
    # Load locations
    locations_df = pd.read_csv('data/locations.csv')
    
    weather_data = []
    
    # Generate data from 2018 to 2023
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    current_date = start_date
    
    while current_date <= end_date:
        for _, location in locations_df.iterrows():
            # Seasonal adjustments
            month = current_date.month
            year = current_date.year
            
            # Base values adjusted by season and location
            if location['coastal'] == 'Yes':
                base_temp = random.uniform(26, 32)
                base_humidity = random.uniform(70, 85)
            else:
                base_temp = random.uniform(28, 36)
                base_humidity = random.uniform(55, 75)
            
            # Seasonal variations
            if month in [3, 4, 5]:  # Summer
                temp_adjust = random.uniform(2, 5)
                humidity_adjust = random.uniform(-15, -5)
                rainfall_base = random.uniform(0, 8)
            elif month in [6, 7, 8, 9]:  # Southwest Monsoon
                temp_adjust = random.uniform(-2, 0)
                humidity_adjust = random.uniform(10, 20)
                rainfall_base = random.uniform(15, 45)
            elif month in [10, 11, 12]:  # Northeast Monsoon
                temp_adjust = random.uniform(-3, -1)
                humidity_adjust = random.uniform(15, 25)
                rainfall_base = random.uniform(25, 65)
            else:  # Winter (Jan, Feb)
                temp_adjust = random.uniform(-4, -1)
                humidity_adjust = random.uniform(0, 10)
                rainfall_base = random.uniform(0, 5)
            
            # Calculate actual values
            temperature = round(base_temp + temp_adjust + random.uniform(-2, 2), 1)
            humidity = round(min(max(base_humidity + humidity_adjust + random.uniform(-5, 5), 30), 100), 1)
            
            # Rainfall varies by location type
            if location['coastal'] == 'Yes':
                rainfall = round(rainfall_base * random.uniform(1.3, 1.8), 1)
            else:
                rainfall = round(rainfall_base * random.uniform(0.7, 1.2), 1)
            
            # Pressure
            pressure = round(random.uniform(1005, 1015) - (rainfall * 0.05), 1)
            
            # Wind
            wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                              'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            
            if month in [10, 11, 12]:  # Northeast Monsoon
                wind_direction = random.choice(['NE', 'NNE', 'ENE', 'N', 'E'])
                wind_speed = round(random.uniform(15, 30), 1)
            elif month in [6, 7, 8, 9]:  # Southwest Monsoon
                wind_direction = random.choice(['SW', 'WSW', 'SSW', 'W', 'S'])
                wind_speed = round(random.uniform(20, 35), 1)
            else:
                wind_direction = random.choice(['SE', 'ESE', 'SSE', 'E', 'S'])
                wind_speed = round(random.uniform(8, 20), 1)
            
            # Cloud cover
            if rainfall > 20:
                cloud_cover = random.randint(70, 100)
            elif rainfall > 10:
                cloud_cover = random.randint(50, 80)
            elif rainfall > 0:
                cloud_cover = random.randint(30, 60)
            else:
                cloud_cover = random.randint(0, 30)
            
            # Evaporation
            evaporation = round(temperature * 0.2 + wind_speed * 0.1 - humidity * 0.05, 1)
            
            weather_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'year': year,
                'month': month,
                'day': current_date.day,
                'location': location['name'],
                'district': location['district'],
                'latitude': location['latitude'],
                'longitude': location['longitude'],
                'coastal': location['coastal'],
                'elevation': location['elevation'],
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'rainfall': max(rainfall, 0),
                'cloud_cover': cloud_cover,
                'evaporation': max(evaporation, 0)
            })
        
        current_date += timedelta(days=1)
        
        # Print progress every 100 days
        if current_date.day == 1:
            print(f"Generated data up to {current_date.strftime('%Y-%m-%d')}")
    
    df = pd.DataFrame(weather_data)
    return df

def add_extreme_weather_events(df):
    """Add extreme weather events (cyclones, heavy rainfall)"""
    
    # Add cyclone events (Northeast monsoon period)
    cyclone_years = [2018, 2020, 2021, 2023]
    cyclone_locations = ['Chennai', 'Cuddalore', 'Nagapattinam', 'Kanyakumari']
    
    for year in cyclone_years:
        for location in cyclone_locations:
            # Random cyclone date in Oct-Dec
            cyclone_date = f"{year}-{random.randint(10, 12)}-{random.randint(10, 20)}"
            
            mask = (df['date'] == cyclone_date) & (df['location'] == location)
            if mask.any():
                df.loc[mask, 'rainfall'] = random.uniform(150, 300)
                df.loc[mask, 'wind_speed'] = random.uniform(60, 100)
                df.loc[mask, 'pressure'] = random.uniform(970, 990)
                df.loc[mask, 'cloud_cover'] = 100
    
    # Add heavy rainfall events
    for _ in range(100):
        random_date = f"{random.randint(2018, 2023)}-{random.randint(6, 12)}-{random.randint(1, 28)}"
        random_location = random.choice(['Chennai', 'Coimbatore', 'Madurai', 'Thanjavur', 'Tirunelveli'])
        
        mask = (df['date'] == random_date) & (df['location'] == random_location)
        if mask.any():
            df.loc[mask, 'rainfall'] = random.uniform(80, 150)
            df.loc[mask, 'wind_speed'] = random.uniform(40, 60)
    
    return df

def add_drought_periods(df):
    """Add drought periods"""
    drought_years = [2019, 2022]
    drought_locations = ['Salem', 'Erode', 'Karur', 'Virudhunagar', 'Ramanathapuram']
    
    for year in drought_years:
        for location in drought_locations:
            for month in [3, 4, 5]:  # Summer months
                for day in range(1, 31):
                    date = f"{year}-{month:02d}-{day:02d}"
                    mask = (df['date'] == date) & (df['location'] == location)
                    if mask.any():
                        df.loc[mask, 'rainfall'] = 0
                        df.loc[mask, 'humidity'] = random.uniform(30, 45)
                        df.loc[mask, 'temperature'] = random.uniform(38, 42)
    
    return df

if __name__ == "__main__":
    print("Generating Tamilnadu weather data...")
    df = generate_tamilnadu_weather_data()
    
    print("Adding extreme weather events...")
    df = add_extreme_weather_events(df)
    
    print("Adding drought periods...")
    df = add_drought_periods(df)
    
    # Save to CSV
    df.to_csv('data/tamilnadu_weather.csv', index=False)
    print(f"\nGenerated {len(df)} weather records")
    print(f"Data saved to data/tamilnadu_weather.csv")
    
    # Display sample
    print("\nSample data:")
    print(df.head(10))
    print(f"\nTotal locations: {df['location'].nunique()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")