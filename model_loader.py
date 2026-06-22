import tensorflow as tf
import numpy as np
import joblib
import os

class ModelLoader:
    def __init__(self):
        self.lstm_model = None
        self.cnn_lstm_model = None
        self.scaler_X = None
        self.scaler_y = None
        self.load_models()
    
    def load_models(self):
        """Load trained models and scalers"""
        model_path = 'models/lstm_rainfall_model.h5'
        cnn_model_path = 'models/cnn_lstm_rainfall_model.h5'
        scaler_X_path = 'models/scaler_X.pkl'
        scaler_y_path = 'models/scaler_y.pkl'
        
        # Load LSTM model if exists
        if os.path.exists(model_path):
            try:
                self.lstm_model = tf.keras.models.load_model(model_path)
                print("LSTM model loaded successfully")
            except Exception as e:
                print(f"Error loading LSTM model: {e}")
        
        # Load CNN-LSTM model if exists
        if os.path.exists(cnn_model_path):
            try:
                self.cnn_lstm_model = tf.keras.models.load_model(cnn_model_path)
                print("CNN-LSTM model loaded successfully")
            except Exception as e:
                print(f"Error loading CNN-LSTM model: {e}")
        
        # Load scalers
        if os.path.exists(scaler_X_path):
            self.scaler_X = joblib.load(scaler_X_path)
            print("Scaler X loaded successfully")
        
        if os.path.exists(scaler_y_path):
            self.scaler_y = joblib.load(scaler_y_path)
            print("Scaler Y loaded successfully")
    
    def predict_with_lstm(self, sequence):
        """Make prediction using LSTM model"""
        if self.lstm_model and self.scaler_X and self.scaler_y:
            try:
                # Scale the input
                sequence_scaled = self.scaler_X.transform(sequence)
                sequence_scaled = sequence_scaled.reshape((1, sequence_scaled.shape[0], sequence_scaled.shape[1]))
                
                # Predict
                prediction_scaled = self.lstm_model.predict(sequence_scaled, verbose=0)
                prediction = self.scaler_y.inverse_transform(prediction_scaled)
                
                return float(prediction[0][0])
            except Exception as e:
                print(f"Error making LSTM prediction: {e}")
                return None
        return None
    
    def predict_with_cnn_lstm(self, sequence):
        """Make prediction using CNN-LSTM model"""
        if self.cnn_lstm_model and self.scaler_X and self.scaler_y:
            try:
                # Scale the input
                sequence_scaled = self.scaler_X.transform(sequence)
                sequence_scaled = sequence_scaled.reshape((1, sequence_scaled.shape[0], sequence_scaled.shape[1]))
                
                # Predict
                prediction_scaled = self.cnn_lstm_model.predict(sequence_scaled, verbose=0)
                prediction = self.scaler_y.inverse_transform(prediction_scaled)
                
                return float(prediction[0][0])
            except Exception as e:
                print(f"Error making CNN-LSTM prediction: {e}")
                return None
        return None
    
    def is_model_available(self):
        """Check if any model is available"""
        return self.lstm_model is not None or self.cnn_lstm_model is not None