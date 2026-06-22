import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

class WeatherPatternAnalyzer:
    def __init__(self):
        self.monsoon_seasons = {
            'northeast': [10, 11, 12],  # October to December
            'southwest': [6, 7, 8, 9],   # June to September
            'summer': [3, 4, 5],         # March to May
            'winter': [1, 2]             # January to February
        }
        
        self.cyclone_prone_areas = [
            'Chennai', 'Cuddalore', 'Kanyakumari', 'Thanjavur', 'Tirunelveli'
        ]
        
    def analyze_rainfall_patterns(self, df):
        """Analyze rainfall patterns across different seasons"""
        patterns = {}
        
        for season, months in self.monsoon_seasons.items():
            season_data = df[df['month'].isin(months)]
            
            patterns[season] = {
                'avg_rainfall': season_data['rainfall'].mean(),
                'max_rainfall': season_data['rainfall'].max(),
                'rainy_days': (season_data['rainfall'] > 0).sum(),
                'avg_temperature': season_data['temperature'].mean(),
                'avg_humidity': season_data['humidity'].mean(),
                'dominant_wind': season_data['wind_direction'].mode().iloc[0] if not season_data.empty else 'N'
            }
        
        return patterns
    
    def detect_cyclone_risk(self, location, weather_data):
        """Detect potential cyclone risk based on weather patterns"""
        risk_score = 0
        risk_factors = []
        
        # Location based risk
        if location in self.cyclone_prone_areas:
            risk_score += 30
            risk_factors.append("Cyclone prone coastal area")
        
        # Weather based risk
        if weather_data['wind_speed'] > 50:
            risk_score += 25
            risk_factors.append("Extreme wind speed")
        elif weather_data['wind_speed'] > 35:
            risk_score += 15
            risk_factors.append("High wind speed")
        
        if weather_data['pressure'] < 990:
            risk_score += 30
            risk_factors.append("Very low pressure")
        elif weather_data['pressure'] < 1000:
            risk_score += 20
            risk_factors.append("Low pressure")
        
        if weather_data['rainfall'] > 50:
            risk_score += 15
            risk_factors.append("Extreme rainfall")
        elif weather_data['rainfall'] > 25:
            risk_score += 10
            risk_factors.append("Heavy rainfall")
        
        # Seasonal risk
        month = datetime.now().month
        if month in [10, 11]:  # Peak cyclone season
            risk_score += 20
            risk_factors.append("Peak cyclone season")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "EXTREME"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'risk_factors': risk_factors,
            'advisory': self.get_cyclone_advisory(risk_level)
        }
    
    def get_cyclone_advisory(self, risk_level):
        """Get appropriate advisory based on risk level"""
        advisories = {
            'LOW': "Normal weather conditions. No immediate threat.",
            'MODERATE': "Monitor weather updates. Prepare emergency kit.",
            'HIGH': "Be alert. Follow local authority instructions. Avoid coastal areas.",
            'EXTREME': "EXTREME DANGER! Evacuate if advised. Stay indoors. Emergency services alerted."
        }
        return advisories.get(risk_level, "No advisory")
    
    def predict_seasonal_trends(self, historical_data, years_ahead=1):
        """Predict seasonal trends for upcoming years"""
        trends = {}
        
        for season, months in self.monsoon_seasons.items():
            season_data = historical_data[historical_data['month'].isin(months)]
            
            if len(season_data) > 0:
                # Simple linear trend analysis
                years = season_data['year'].unique()
                avg_rainfall_by_year = season_data.groupby('year')['rainfall'].mean()
                
                if len(avg_rainfall_by_year) > 1:
                    # Calculate trend
                    x = np.arange(len(avg_rainfall_by_year))
                    y = avg_rainfall_by_year.values
                    slope = np.polyfit(x, y, 1)[0]
                    
                    # Predict next year
                    last_year_rainfall = avg_rainfall_by_year.iloc[-1]
                    predicted_rainfall = last_year_rainfall + slope
                else:
                    predicted_rainfall = season_data['rainfall'].mean()
                
                trends[season] = {
                    'predicted_rainfall': max(predicted_rainfall, 0),
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'confidence': min(abs(slope) * 10, 90) if 'slope' in locals() else 50
                }
        
        return trends
    
    def cluster_weather_patterns(self, df, n_clusters=4):
        """Cluster weather patterns using K-means"""
        # Select features for clustering
        features = ['temperature', 'humidity', 'pressure', 'wind_speed', 'rainfall']
        
        # Prepare data
        X = df[features].dropna()
        
        if len(X) >= n_clusters:
            # Normalize data
            X_normalized = (X - X.mean()) / X.std()
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_normalized)
            
            # Reduce dimensionality for visualization
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_normalized)
            
            # Describe clusters
            cluster_descriptions = {}
            for i in range(n_clusters):
                cluster_data = X[clusters == i]
                cluster_descriptions[f'Cluster {i+1}'] = {
                    'size': len(cluster_data),
                    'avg_rainfall': cluster_data['rainfall'].mean(),
                    'avg_temperature': cluster_data['temperature'].mean(),
                    'avg_humidity': cluster_data['humidity'].mean(),
                    'characteristics': self.describe_cluster(cluster_data)
                }
            
            return {
                'clusters': cluster_descriptions,
                'pca_components': X_pca.tolist(),
                'labels': clusters.tolist()
            }
        
        return None
    
    def describe_cluster(self, cluster_data):
        """Describe the characteristics of a cluster"""
        rainfall = cluster_data['rainfall'].mean()
        temp = cluster_data['temperature'].mean()
        
        if rainfall > 20:
            return "Heavy rainfall zone"
        elif rainfall > 10:
            return "Moderate rainfall zone"
        elif rainfall > 2:
            return "Light rainfall zone"
        else:
            return "Dry zone"
    
    def calculate_drought_index(self, historical_data):
        """Calculate drought severity index"""
        # Simplified SPI (Standardized Precipitation Index) calculation
        monthly_rainfall = historical_data.groupby('month')['rainfall'].mean()
        overall_mean = historical_data['rainfall'].mean()
        overall_std = historical_data['rainfall'].std()
        
        drought_status = {}
        
        for month in range(1, 13):
            month_data = historical_data[historical_data['month'] == month]
            if len(month_data) > 0:
                current_rainfall = month_data['rainfall'].iloc[-1] if len(month_data) > 0 else 0
                
                # Calculate SPI-like index
                if overall_std > 0:
                    spi = (current_rainfall - overall_mean) / overall_std
                else:
                    spi = 0
                
                # Classify drought severity
                if spi <= -2:
                    severity = "Extreme Drought"
                elif spi <= -1.5:
                    severity = "Severe Drought"
                elif spi <= -1:
                    severity = "Moderate Drought"
                elif spi <= -0.5:
                    severity = "Mild Drought"
                else:
                    severity = "Normal"
                
                drought_status[month] = {
                    'spi': round(spi, 2),
                    'severity': severity,
                    'rainfall_deficit': round(((current_rainfall - monthly_rainfall[month]) / monthly_rainfall[month]) * 100, 1) if monthly_rainfall[month] > 0 else 0
                }
        
        return drought_status