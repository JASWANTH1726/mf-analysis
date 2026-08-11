import pandas as pd
from src.data_preprocessing import DataPreprocessor
from src.model_training import ModelTrainer
from sklearn.model_selection import train_test_split

def main():
    # Load sample data (replace with your actual data)
    # For demo, we'll create synthetic data
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])
    df['target'] = y
    
    # Preprocess data
    preprocessor = DataPreprocessor()
    X_processed, y_processed = preprocessor.preprocess(df, 'target')
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
    
    # Train model
    trainer = ModelTrainer()
    model = trainer.train(X_train, y_train)
    
    # Evaluate model
    accuracy = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model('models/trained_model.pkl')
    
    print(f"Training completed. Model accuracy: {accuracy}")

if __name__ == "__main__":
    main()