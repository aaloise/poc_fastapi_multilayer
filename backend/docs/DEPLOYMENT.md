# 🚀 Deployment — Guia de Deploy

## Visão Geral

Este guia cobre diferentes formas de fazer deploy da aplicação em produção.

## Opções de Deploy

| Opção | Complexidade | Custo | Controle |
|-------|--------------|-------|----------|
| **Docker** | Baixa | Baixo | Médio |
| **Docker Compose** | Baixa | Baixo | Alto |
| **Kubernetes** | Alta | Médio | Total |
| **Cloud (AWS/GCP)** | Média | Variável | Alto |
| **Railway/Render** | Baixa | Baixo | Baixo |

## Docker

### Dockerfile

```dockerfile
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* granian.toml ./
COPY src/ ./src/

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Run with Granian + uvloop
CMD ["uv", "run", "granian", "--interface", "asgi", "--config", "granian.toml", "app.main:app"]
```

### Build e Run

```bash
# Build
docker build -t async-poc .

# Run
docker run -d \
  --name async-poc \
  -p 8000:8000 \
  -e POC_DEBUG=false \
  -e POC_DB_URL=sqlite+aiosqlite:///./data/poc.db \
  -v $(pwd)/data:/app/data \
  async-poc

# Logs
docker logs -f async-poc

# Stop
docker stop async-poc
docker rm async-poc
```

### Multi-stage Build (otimizado)

```dockerfile
# Build stage
FROM python:3.13-slim as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

# Runtime stage
FROM python:3.13-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY granian.toml ./

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["granian", "--interface", "asgi", "--config", "granian.toml", "app.main:app"]
```

## Docker Compose

### docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POC_DEBUG=false
      - POC_DB_URL=sqlite+aiosqlite:///./data/poc.db
      - POC_QUEUE_CONCURRENCY=8
    volumes:
      - app-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G

  # Optional: Prefect server
  prefect:
    image: prefecthq/prefect:3-python3.14
    ports:
      - "4200:4200"
    environment:
      - PREFECT_SERVER_API_HOST=0.0.0.0
    profiles:
      - prefect

  # Optional: Redis (for Queuefy)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    profiles:
      - redis

volumes:
  app-data:
```

### Comandos

```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f app

# Stop
docker-compose down

# With Prefect
docker-compose --profile prefect up -d

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Kubernetes

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: async-poc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: async-poc
  template:
    metadata:
      labels:
        app: async-poc
    spec:
      containers:
      - name: app
        image: your-registry/async-poc:latest
        ports:
        - containerPort: 8000
        env:
        - name: POC_DEBUG
          value: "false"
        - name: POC_DB_URL
          valueFrom:
            secretKeyRef:
              name: async-poc-secrets
              key: db-url
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: async-poc
spec:
  selector:
    app: async-poc
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: async-poc
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: async-poc
            port:
              number: 80
  tls:
  - hosts:
    - api.example.com
    secretName: tls-secret
```

### Deploy

```bash
# Apply
kubectl apply -f k8s/

# Check
kubectl get pods
kubectl get services
kubectl get ingress

# Logs
kubectl logs -f deployment/async-poc

# Scale
kubectl scale deployment/async-poc --replicas=5
```

## Cloud Providers

### AWS ECS

```bash
# Push image
aws ecr create-repository --repository-name async-poc
docker tag async-poc:latest <account>.dkr.ecr.<region>.amazonaws.com/async-poc:latest
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker push <account>.dkr.ecr.<region>.amazonaws.com/async-poc:latest

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster my-cluster \
  --service-name async-poc \
  --task-definition async-poc \
  --desired-count 3
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/async-poc

# Deploy
gcloud run deploy async-poc \
  --image gcr.io/PROJECT_ID/async-poc \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars POC_DEBUG=false
```

### Railway

```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Init
railway init

# Deploy
railway up

# Set env vars
railway variables set POC_DEBUG=false
```

## Environment Variables

### Produção

```bash
# .env.production
POC_DEBUG=false
POC_HOST=0.0.0.0
POC_PORT=8000
POC_DB_URL=postgresql+asyncpg://user:pass@host:5432/dbname
POC_QUEUE_CONCURRENCY=16
POC_UI_PREFIX=/ui
```

### Staging

```bash
# .env.staging
POC_DEBUG=true
POC_HOST=0.0.0.0
POC_PORT=8000
POC_DB_URL=postgresql+asyncpg://user:pass@staging-host:5432/dbname
POC_QUEUE_CONCURRENCY=8
```

## Database Migration

### PostgreSQL

```bash
# Install asyncpg
uv add asyncpg

# Update .env
POC_DB_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb

# Create database
createdb mydb

# Tables created automatically on startup
```

### Alembic (migrations)

```bash
# Install
uv add alembic

# Init
alembic init alembic

# Configure
# Edit alembic.ini and alembic/env.py

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply
alembic upgrade head
```

## Reverse Proxy

### Nginx

```nginx
upstream async_poc {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://async_poc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Caddy

```
api.example.com {
    reverse_proxy localhost:8000
}
```

## SSL/TLS

### Let's Encrypt (Certbot)

```bash
# Install
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.example.com

# Auto-renew
sudo certbot renew --dry-run
```

### Caddy (automatic)

```
api.example.com {
    reverse_proxy localhost:8000
}
# Caddy automatically gets SSL from Let's Encrypt
```

## Monitoring

### Health Check

```bash
# Endpoint
curl http://localhost:8000/api/v1/health

# Response
{
    "status": "healthy",
    "version": "0.1.0",
    "timestamp": "2026-01-15T10:30:00",
    "components": {
        "fastapi": true,
        "database": true,
        "queuefy": true,
        "prefect": true,
        "nicegui": true,
        "uvloop": true
    }
}
```

### Logs

```bash
# Structured logs (JSON)
uv run granian app.main:app --log-dict-config '{"format": "json"}'

# Send to ELK/Loki
# Configure log shipping
```

### Metrics

```python
# Add prometheus-client
uv add prometheus-client

# Expose metrics
from prometheus_client import generate_latest, Counter

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Security Checklist

- ✅ Use HTTPS (SSL/TLS)
- ✅ Set `POC_DEBUG=false`
- ✅ Use strong database passwords
- ✅ Enable CORS only for specific domains
- ✅ Use environment variables for secrets
- ✅ Regular security updates
- ✅ Rate limiting
- ✅ Input validation
- ✅ SQL injection prevention (use ORM)
- ✅ XSS prevention
- ✅ CSRF protection
- ✅ Content Security Policy headers

## Performance Tuning

### Granian

```toml
# granian.toml
workers = 8  # 2-4x CPU cores
threads = 4  # For I/O-bound
backpressure = 2048
```

### Database

```python
# Connection pooling
_engine = create_async_engine(
    url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching

```python
# Add redis for caching
uv add redis

from redis.asyncio import Redis

redis = Redis.from_url("redis://localhost:6379")

@router.get("/tasks/{task_id}")
async def get_task(task_id: uuid.UUID):
    # Check cache
    cached = await redis.get(f"task:{task_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    task = await get_task_by_id(task_id)
    
    # Cache for 5 minutes
    await redis.setex(f"task:{task_id}", 300, json.dumps(task.dict()))
    
    return task
```

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t async-poc .
    
    - name: Push to registry
      run: |
        docker tag async-poc registry.example.com/async-poc:latest
        docker push registry.example.com/async-poc:latest
    
    - name: Deploy to production
      run: |
        # Your deployment script
        kubectl set image deployment/async-poc app=registry.example.com/async-poc:latest
```

## Troubleshooting

### App não inicia

```bash
# Check logs
docker logs async-poc

# Check health
curl http://localhost:8000/api/v1/health

# Check database connection
psql $POC_DB_URL -c "SELECT 1"
```

### Lentidão

```bash
# Check workers
docker stats async-poc

# Check database
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'pending';

# Check Queuefy
SELECT COUNT(*) FROM queuefy_runs WHERE status = 'pending';
```

### Memory leak

```bash
# Monitor memory
docker stats async-poc

# Profile
uv run python -m memory_profiler app/main.py
```

## Links

- [Docker Docs](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
