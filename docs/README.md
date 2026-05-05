# ML Project Documentation

## Overview
This project implements a complete ML pipeline with deployment and MLOps capabilities.

## Architecture
- Data preprocessing with scikit-learn
- Model training with Random Forest
- API deployment with FastAPI
- Containerization with Docker
- Orchestration with Kubernetes
- Experiment tracking with MLflow
- Data versioning with DVC

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the training pipeline: `python src/train.py`
4. Start the API: `uvicorn src.api:app --reload`
5. Access the API at http://localhost:8000

## API Endpoints
- `POST /predict`: Make predictions
- `GET /health`: Health check

## Deployment
- Local: `docker-compose up`
- Kubernetes: Apply manifests in `k8s/` directory

## MLOps
- Track experiments with MLflow
- Version data with DVC
- CI/CD with GitHub Actions