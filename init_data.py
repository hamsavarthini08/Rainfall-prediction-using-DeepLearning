import json
import os
import pandas as pd
import numpy as np
from models.generate_training_data import TrainingDataGenerator
from data.generate_weather_csv import generate_tamilnadu_weather_data, add_extreme_weather_events, add_drought_periods

def initialize_data():
    """Initialize all data files"""
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Generate locations.csv if it doesn't exist
    if not os.path.exists('data/locations.csv'):
        print("Generating locations.csv...")
        locations_data = {
            'name': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem', 
                    'Tirunelveli', 'Vellore', 'Erode', 'Thanjavur', 'Kanyakumari',
                    'Virudhunagar', 'Dindigul', 'Cuddalore', 'Kanchipuram', 'Namakkal'],
            'district': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem',
                        'Tirunelveli', 'Vellore', 'Erode', 'Thanjavur', 'Kanyakumari',
                        'Virudhunagar', 'Dindigul', 'Cuddalore', 'Kanchipuram', 'Namakkal'],
            'latitude': [13.0827, 11.0168, 9.9252, 10.7905, 11.6643,
                        8.7139, 12.9165, 11.3410, 10.7870, 8.0883,
                        9.5680, 10.3624, 11.7446, 12.8342, 11.2210],
            'longitude': [80.2707, 76.9558, 78.1198, 78.7047, 78.1460,
                         77.7567, 79.1325, 77.7172, 79.1378, 77.5385,
                         77.9624, 77.9695, 79.7685, 79.7038, 78.1674],
            'coastal': ['Yes', 'No', 'No', 'No', 'No',
                       'Yes', 'No', 'No', 'Yes', 'Yes',
                       'No', 'No', 'Yes', 'Yes', 'No'],
            'elevation': [6, 411, 101, 88, 278,
                         47, 216, 183, 88, 30,
                         102, 268, 6, 83, 225],
            'population_density': [26903, 6823, 8232, 5832, 4598,
                                  4582, 3456, 3876, 4231, 4567,
                                  3890, 3456, 4567, 2345, 3890],
            'region': ['North East', 'West', 'South Central', 'Central', 'West',
                      'South', 'North', 'West', 'East', 'South',
                      'South', 'South Central', 'East', 'North', 'West']
        }
        
        locations_df = pd.DataFrame(locations_data)
        locations_df.to_csv('data/locations.csv', index=False)
        print("locations.csv generated successfully!")
    else:
        print("Loading existing locations.csv...")
        locations_df = pd.read_csv('data/locations.csv')
    
    # Generate tamilnadu_weather.csv
    print("\nGenerating tamilnadu_weather.csv (this may take a few minutes)...")
    df = generate_tamilnadu_weather_data()
    
    print("Adding extreme weather events...")
    df = add_extreme_weather_events(df)
    
    print("Adding drought periods...")
    df = add_drought_periods(df)
    
    # Save to CSV
    df.to_csv('data/tamilnadu_weather.csv', index=False)
    print(f"\nGenerated {len(df)} weather records")
    print(f"Data saved to data/tamilnadu_weather.csv")
    
    # Generate training data for model
    print("\nGenerating training data for model...")
    generator = TrainingDataGenerator()
    training_df = generator.generate_historical_data(2010, 2023)
    training_df.to_csv('data/training_data.csv', index=False)
    print(f"Generated {len(training_df)} training records")
    
    # Create locations.json from locations.csv
    print("\nGenerating locations.json...")
    locations_dict = {}
    for _, row in locations_df.iterrows():
        locations_dict[row['name']] = {
            'lat': row['latitude'],
            'lon': row['longitude'],
            'district': row['district'],
            'coastal': row['coastal'],
            'elevation': row['elevation']
        }
    
    with open('data/locations.json', 'w') as f:
        json.dump(locations_dict, f, indent=4)
    print("locations.json generated successfully!")
    
    # Create summary report
    print("\n" + "="*50)
    print("DATA INITIALIZATION COMPLETE")
    print("="*50)
    print(f"Locations CSV: {len(locations_df)} locations")
    print(f"Weather CSV: {len(df)} records")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Training CSV: {len(training_df)} records")
    print("\nFiles created:")
    print("  - data/locations.csv")
    print("  - data/locations.json")
    print("  - data/tamilnadu_weather.csv")
    print("  - data/training_data.csv")
    
    return True

if __name__ == "__main__":
    initialize_data()