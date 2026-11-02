# Lab 11 — Deployment and Debugging Report

## 1. Objective

The objective of this activity was to simulate deployment failures,
identify their root causes, debug the failures using container logs
and status information, recover the deployment, and validate
Kubernetes self-healing behavior.

---

## 2. Deployment Environment

### Docker

Docker was used to package and execute the Churn Prediction API.

Docker image:

churn-prediction-api:1.0

Application:

FastAPI

Application port:

8000

### Kubernetes

Kubernetes was provided through Docker Desktop using Kind.

Kubernetes version:

v1.36.1

Node:

desktop-control-plane

Node status:

Ready

---

# 3. Failure Scenario 1 — Missing Model Artifact

## 3.1 Failure Injection

A missing model artifact was intentionally simulated by renaming
the model inside the running container.

Command:

docker exec churn-api mv /app/deployment/model.pkl /app/deployment/model_backup.pkl

The container was then restarted:

docker restart churn-api

---

## 3.2 Failure Observed

During application startup, ModelLoader attempted to load:

/app/deployment/model.pkl

The application produced:

FileNotFoundError: Model not found: /app/deployment/model.pkl

The FastAPI application failed during startup.

---

# 4. Failure Detection

The container status was inspected using:

docker ps -a --filter "name=churn-api"

The container was found in the following state:

Exited (3)

The exact state was confirmed using:

docker inspect churn-api --format "{{.State.Status}} | ExitCode={{.State.ExitCode}}"

Result:

exited | ExitCode=3

The container could not be inspected using docker exec because
the container was no longer running.

---

# 5. Root Cause Analysis

The root cause was a missing required model artifact.

Expected:

/app/deployment/model.pkl

Actual:

The file had been renamed to:

/app/deployment/model_backup.pkl

ModelLoader checks for the required model file before loading it.

Because the file did not exist at the expected path, ModelLoader
raised FileNotFoundError and FastAPI startup failed.

Root cause:

Missing deployment model artifact.

---

# 6. Log-Based Debugging

Docker logs were inspected using:

docker logs --tail 30 churn-api

The important error was:

FileNotFoundError: Model not found:
/app/deployment/model.pkl

The traceback showed the failure path:

FastAPI lifespan
    ↓
model_loader.load()
    ↓
load_deployment_bundle()
    ↓
Missing model.pkl
    ↓
FileNotFoundError
    ↓
Application startup failed

This allowed the failure to be traced from the application
startup process to the missing artifact.

---

# 7. Deployment Recovery

Instead of manually modifying the corrupted container, the
failed container was removed.

Command:

docker rm churn-api

The container was recreated from the known-good Docker image:

docker run --name churn-api -p 8000:8000 churn-prediction-api:1.0

The original Docker image was not modified during the failure
simulation.

---

# 8. Recovery Result

After recreating the container, the application successfully
loaded the deployment bundle.

Successful messages included:

[SUCCESS] Model loaded successfully.

[SUCCESS] Preprocessor loaded successfully.

[SUCCESS] ModelLoader initialization completed.

FastAPI successfully reached:

Application startup complete.

Uvicorn running on:

http://0.0.0.0:8000

The deployment was successfully recovered.

---

# 9. Kubernetes Failure Scenario

After successful Kubernetes deployment, the application was
scaled to three replicas.

Command:

kubectl scale deployment churn-api --replicas=3

Result:

3/3 replicas available.

Three Pods were running.

---

# 10. Kubernetes Service Interruption

One running Pod was intentionally deleted.

Command:

kubectl delete pod churn-api-84f5fcd955-cc6gt

The deleted Pod was:

churn-api-84f5fcd955-cc6gt

---

# 11. Kubernetes Failure Detection

The Deployment had a desired replica count of:

3

After deleting one Pod, the actual number of running Pods
temporarily became:

2

Kubernetes detected the difference between the desired and
actual state.

The Deployment controller automatically created a replacement Pod.

Replacement Pod:

churn-api-84f5fcd955-llpfs

---

# 12. Kubernetes Recovery

After recovery, three Pods were running:

churn-api-84f5fcd955-j5nqm
churn-api-84f5fcd955-kdj9j
churn-api-84f5fcd955-llpfs

Deployment status:

3/3 READY
3/3 UP-TO-DATE
3/3 AVAILABLE

This demonstrated Kubernetes self-healing behavior.

---

# 13. Kubernetes Service Recovery

The Kubernetes Service was:

churn-api-service

Service type:

NodePort

Service port:

8000

NodePort:

30383

After Pod recovery, the Service had three active endpoints:

10.244.0.5:8000
10.244.0.6:8000
10.244.0.8:8000

This confirmed that the Service recognized the recovered
application replicas.

---

# 14. Application-Level Recovery Validation

The Kubernetes Service was accessed using port forwarding:

kubectl port-forward service/churn-api-service 8000:8000

The health endpoint was tested:

GET /health

Result:

healthy

The metadata endpoint was tested:

GET /metadata

Result:

service             : Churn Prediction API
version             : 1.0.0
model_name          : Telco_Churn_Production_Model
model_uri           : /app/deployment/model.pkl
model_loaded        : True
preprocessor_loaded : True

Therefore, the recovered Kubernetes deployment was operational
at the application level.

---

# 15. Failure → Debugging → Recovery Flow

## Docker Failure

Missing model artifact
        ↓
FastAPI startup failure
        ↓
FileNotFoundError
        ↓
Container exited with code 3
        ↓
Docker logs inspected
        ↓
Root cause identified
        ↓
Broken container removed
        ↓
Known-good image used
        ↓
Container recreated
        ↓
API recovered

---

## Kubernetes Failure

3 running Pods
        ↓
1 Pod intentionally deleted
        ↓
2 Pods temporarily available
        ↓
Deployment detects replica mismatch
        ↓
Replacement Pod created
        ↓
3 Pods running again
        ↓
Service has 3 endpoints
        ↓
/health = healthy
        ↓
/metadata confirms model loaded

---

# 16. Debugging Tools Used

The following commands were used during failure analysis:

docker ps -a

docker inspect churn-api

docker logs churn-api

docker rm churn-api

kubectl get deployments

kubectl get pods

kubectl get endpoints churn-api-service

kubectl describe service churn-api-service

kubectl delete pod <pod-name>

kubectl get pods -w

kubectl port-forward service/churn-api-service 8000:8000

---

# 17. Findings

### Docker

The containerized application failed when a required deployment
artifact was missing.

The failure was detected through:

- Container status
- Exit code
- Docker logs
- Application traceback

The deployment was restored by recreating the container from the
known-good Docker image.

### Kubernetes

Kubernetes maintained the desired replica count after a Pod was
deleted.

The Deployment automatically created a replacement Pod.

The Service continued to provide access to healthy Pods.

---

# 18. Validation Summary

| Validation | Result |
|---|---|
| Docker failure simulated | PASS |
| Missing artifact detected | PASS |
| Root cause identified | PASS |
| Docker deployment recovered | PASS |
| Kubernetes deployment running | PASS |
| Kubernetes scaled to 3 replicas | PASS |
| Pod interruption simulated | PASS |
| Replacement Pod created | PASS |
| 3/3 replicas restored | PASS |
| Service endpoints restored | PASS |
| /health validated | PASS |
| /metadata validated | PASS |

---

# 19. Conclusion

The deployment failure and debugging exercises demonstrated that
ML deployment failures can be detected using container state,
exit codes, application logs, and Kubernetes workload status.

The Docker deployment was recovered by recreating the application
from a known-good immutable image.

The Kubernetes deployment demonstrated automatic Pod recovery
when a running Pod was intentionally deleted.

The final application-level validation confirmed that the
recovered service was healthy and that the Production model and
preprocessor were successfully loaded.

This completes the deployment failure, debugging, and recovery
requirements of Lab 11.
---

# 20. Additional Kubernetes Scaling and Recovery Validation

## 20.1 Kubernetes Environment

The Kubernetes environment was verified using Docker Desktop.

Kubernetes context:

docker-desktop

Kubernetes version:

v1.36.1

Node:

desktop-control-plane

Node status:

Ready

Docker image:

churn-prediction-api:lab10

## 20.2 Kubernetes Service Configuration

Service name:

churn-api-service

Service type:

NodePort

Service port:

8000

NodePort:

31202

The API was accessed locally using port forwarding:

kubectl port-forward service/churn-api-service 8003:8000

Swagger documentation:

http://127.0.0.1:8003/docs

## 20.3 Scaling Validation

The deployment was scaled from one replica to two and then three replicas.

Commands:

kubectl scale deployment churn-api --replicas=2

kubectl scale deployment churn-api --replicas=3

Final deployment status:

3/3 READY
3/3 UP-TO-DATE
3/3 AVAILABLE

All three Pods reached Running status.

## 20.4 Pod Interruption and Automatic Recovery

One running Pod was intentionally deleted.

Command:

kubectl delete pod churn-api-58f884d7d6-4q5l4

Kubernetes automatically created a replacement Pod:

churn-api-58f884d7d6-dnr8r

After recovery:

3/3 READY
3/3 UP-TO-DATE
3/3 AVAILABLE

All three Pods were Running.

This confirmed Kubernetes Deployment controller self-healing.

## 20.5 Deployment Scale-Down and Restoration

The entire deployment was temporarily scaled down to zero replicas.

Command:

kubectl scale deployment churn-api --replicas=0

Observed result:

0/0 READY

No application Pods remained in the default namespace.

The deployment was then restored to three replicas.

Command:

kubectl scale deployment churn-api --replicas=3

Recovery result:

3/3 READY
3/3 UP-TO-DATE
3/3 AVAILABLE

Three new Pods were created and reached Running status.

This demonstrated successful recovery after complete application scale-down.

## 20.6 API Validation After Recovery

The Kubernetes Service was accessed through port forwarding.

Swagger documentation was available at:

http://127.0.0.1:8003/docs

The following endpoints were tested:

GET /health

Result:

HTTP 200
{
  "status": "healthy"
}

POST /predict

Result:

Prediction request executed successfully.

The API remained operational after the deployment was restored to three replicas.

## 20.7 Additional Validation Summary

| Validation | Result |
|---|---|
| Kubernetes context verified | PASS |
| Kubernetes node Ready | PASS |
| Deployment scaled to 2 replicas | PASS |
| Deployment scaled to 3 replicas | PASS |
| All 3 Pods Running | PASS |
| Pod deletion simulated | PASS |
| Replacement Pod created | PASS |
| Deployment restored to 3/3 | PASS |
| Deployment scaled down to 0 | PASS |
| No Pods after scale-down | PASS |
| Deployment restored from 0 to 3 | PASS |
| Health endpoint after recovery | PASS |
| Prediction endpoint after recovery | PASS |
| Swagger documentation accessible | PASS |

## 20.8 Conclusion

Additional Kubernetes experiments confirmed that the Churn Prediction API can be scaled horizontally, recover automatically from individual Pod deletion, and be restored after the entire Deployment is scaled down to zero.

The Kubernetes Service continued to provide access to the application after recovery. Health and prediction requests were successfully validated.

These experiments demonstrate Kubernetes scaling, workload reconciliation, self-healing, and application recovery capabilities.
