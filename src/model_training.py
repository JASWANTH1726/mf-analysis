import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import mlflow
import mlflow.sklearn

class ModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def train(self, X_train, y_train):
        with mlflow.start_run():
            self.model.fit(X_train, y_train)
            
            # Log parameters
            mlflow.log_param("n_estimators", 100)
            mlflow.log_param("random_state", 42)
            
            # Log model
            mlflow.sklearn.log_model(self.model, "model")
        
        return self.model
    
    def evaluate(self, X_test, y_test):
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        with mlflow.start_run():
            mlflow.log_metric("accuracy", accuracy)
        
        print(f"Accuracy: {accuracy}")
        print(classification_report(y_test, predictions))
        
        return accuracy
    
    def save_model(self, path):
        joblib.dump(self.model, path)
    
    def load_model(self, path):
        self.model = joblib.load(path)
        return self.model