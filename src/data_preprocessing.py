import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}
    
    def preprocess(self, df, target_col):
        # Handle missing values
        df = df.dropna()
        
        # Encode categorical variables
        for col in df.select_dtypes(include=['object']):
            if col != target_col:
                self.encoders[col] = LabelEncoder()
                df[col] = self.encoders[col].fit_transform(df[col])
        
        # Split features and target
        X = df.drop(target_col, axis=1)
        y = df[target_col]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y
    
    def preprocess_new_data(self, df):
        # Apply same preprocessing to new data
        for col, encoder in self.encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col])
        
        return self.scaler.transform(df)