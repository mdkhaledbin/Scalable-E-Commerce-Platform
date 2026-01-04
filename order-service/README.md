## Order Service

Lightweight FastAPI service that handles order management for the ecommerce platform.

### Local Development

- Install dependencies: `pip install -r requirements.txt`
- Run the API: `uvicorn order-service.main:app --reload --port 8004`
- API docs available at http://localhost:8004/docs while the server is running.

### Docker

- Build the image: `docker build -t order-service .`
- Start the container: `docker run -p 8004:8004 order-service`

### Kubernetes

- Update the image reference in `k8s/deployment.yaml` if needed.
- Apply manifests: `kubectl apply -f k8s/`
- Service exposes port 80 inside the cluster and forwards to container port 8004.
