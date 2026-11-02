# LAB 10 – Production Model Deployment Report

## 1. Objective
The objective of Lab 10 was to retrieve the production Churn Prediction model from the MLflow Model Registry and prepare it for deployment.

## 2. Model Details
- Project: Telco Customer Churn Prediction
- Model name: Telco_Churn_Production_Model
- Model version: 2
- Model stage: Production
- Algorithm: Random Forest Classifier

## 3. Deployment Activities
1. Connected to the local MLflow tracking database.
2. Retrieved the Production model from the MLflow Model Registry.
3. Downloaded the matching preprocessing pipeline.
4. Exported the model as deployment/model.pkl.
5. Exported the preprocessor as deployment/preprocessor.pkl.
6. Generated deployment/model_metadata.json.
7. Loaded and verified both exported artifacts.

## 4. Validation Results
- MLflow Production model retrieved: PASS
- Model export: PASS
- Preprocessor export: PASS
- Metadata creation: PASS
- Model loading verification: PASS
- Preprocessor loading verification: PASS

## 5. Conclusion
The Telco_Churn_Production_Model version 2 was successfully retrieved from MLflow Production stage. The model and matching preprocessing pipeline were exported and verified for API deployment.

## 6. Docker Containerization and Testing

- Docker image: churn-prediction-api:lab10
- Docker container: churn-api-lab10
- Host port: 8002
- Container port: 8000
- Docker image build: PASS
- Container startup: PASS
- Model loading inside container: PASS
- Preprocessor loading inside container: PASS
- Container API root endpoint: PASS
- Container single prediction: PASS
- Container batch prediction: PASS

## 7. Final Conclusion

The Churn Prediction API was successfully containerized using Docker. Both single-customer and batch predictions were tested successfully inside the running container. The deployment is ready for the next stage of the MLOps workflow.
