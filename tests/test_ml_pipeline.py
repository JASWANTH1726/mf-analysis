import pytest
from src.data_preprocessing import DataPreprocessor
from src.model_training import ModelTrainer
import pandas as pd
import numpy as np

def test_data_preprocessing():
    # Create sample data
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': ['A', 'B', 'A', 'B', 'A'],
        'target': [0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    
    preprocessor = DataPreprocessor()
    X, y = preprocessor.preprocess(df, 'target')
    
    assert X.shape == (5, 2)
    assert len(y) == 5

def test_model_training():
    # Create sample data
    X = np.random.rand(100, 5)
    y = np.random.randint(0, 2, 100)
    
    trainer = ModelTrainer()
    model = trainer.train(X, y)
    
    assert model is not None
    assert hasattr(model, 'predict')