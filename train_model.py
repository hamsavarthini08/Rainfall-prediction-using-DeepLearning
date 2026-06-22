import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Conv1D, MaxPooling1D, Flatten, Reshape
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib

class RainfallLSTMModel:
    def __init__(self, sequence_length=30):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
    
    def prepare_data(self, data_path):
        """Prepare data for LSTM training"""
        df = pd.read_csv(data_path)
        
        # Select features
        feature_columns = ['temperature', 'humidity', 'pressure', 
                          'wind_speed', 'wind_direction_encoded', 
                          'latitude', 'longitude', 'month', 'day']
        
        target_column = ['rainfall']
        
        # Encode wind direction
        wind_directions = {'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
                          'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
                          'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
                          'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5}
        
        df['wind_direction_encoded'] = df['wind_direction'].map(wind_directions)
        
        # Extract date features
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Scale features
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y)
        
        # Create sequences
        X_seq, y_seq = self.create_sequences(X_scaled, y_scaled)
        
        return train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)
    
    def create_sequences(self, X, y):
        """Create sequences for LSTM"""
        X_seq, y_seq = [], []
        
        for i in range(len(X) - self.sequence_length):
            X_seq.append(X[i:(i + self.sequence_length)])
            y_seq.append(y[i + self.sequence_length])
        
        return np.array(X_seq), np.array(y_seq)
    
    def build_lstm_model(self, input_shape):
        """Build LSTM model"""
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(100, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def build_cnn_lstm_model(self, input_shape):
        """Build CNN-LSTM hybrid model"""
        model = Sequential([
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=32, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(25, return_sequences=False),
            Dropout(0.2),
            Dense(10, activation='relu'),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100):
        """Train the model"""
        input_shape = (X_train.shape[1], X_train.shape[2])
        
        # Choose model type
        self.model = self.build_cnn_lstm_model(input_shape)
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        checkpoint = ModelCheckpoint(
            'models/lstm_rainfall_model.h5',
            monitor='val_loss',
            save_best_only=True
        )
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=[early_stopping, checkpoint],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """Make predictions"""
        predictions = self.model.predict(X)
        return self.scaler_y.inverse_transform(predictions)

# Training script
if __name__ == "__main__":
    # Initialize model
    model = RainfallLSTMModel(sequence_length=30)
    
    # Prepare data
    X_train, X_test, y_train, y_test = model.prepare_data('data/tamilnadu_weather.csv')
    
    # Train model
    history = model.train(X_train, y_train, X_test, y_test, epochs=50)
    
    # Save scalers
    joblib.dump(model.scaler_X, 'models/scaler_X.pkl')
    joblib.dump(model.scaler_y, 'models/scaler_y.pkl')
    
    print("Model training completed!")