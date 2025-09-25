# KRAI Engine - Deployment Guide

**Complete Guide for Production Deployment**

## Deployment Architecture

The KRAI Engine supports multiple deployment scenarios from local development to enterprise cloud deployment.

## Environment Configuration

### Single Source of Truth

All configuration is managed through the central `.env` file in the project root directory.

```bash
/Users/your-user/krai-engine/.env
```

### Environment Variables Reference

#### Database Configuration
```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://postgres:password@host:port/database
```

#### Supabase Configuration
```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_STORAGE_URL=http://127.0.0.1:54321/storage/v1
```

#### API Configuration
```env
KRAI_API_HOST=0.0.0.0
KRAI_API_PORT=8001
KRAI_API_WORKERS=6
```

#### AI Models Configuration
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=llava:7b
OLLAMA_EMBEDDING_MODEL=embeddinggemma
OLLAMA_TIMEOUT=300
```

#### Performance Configuration
```env
ML_DEVICE=mps
ML_DEVICE_NAME=Apple_Metal_Performance_Shaders
ML_MEMORY_GB=16
ML_BATCH_SIZE=32
ML_CONCURRENT_DOCUMENTS=3
```

## Deployment Scenarios

### Scenario 1: Local Development

Complete local setup for development and testing.

**Components:**
- Database: Local Supabase (Docker)
- AI Models: Local Ollama
- API: Local FastAPI server

**Setup:**
```bash
# Start local Supabase
supabase start

# Configure .env for local
SUPABASE_URL=http://127.0.0.1:54321
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54322
OLLAMA_BASE_URL=http://localhost:11434
```

**Start Services:**
```bash
cd backend
python3 production_main.py
```

### Scenario 2: Hybrid Cloud

Database in cloud, AI processing local.

**Components:**
- Database: Supabase Cloud
- AI Models: Local Ollama (GPU workstation)
- API: Local or cloud

**Setup:**
```bash
# Configure .env for hybrid
SUPABASE_URL=https://your-project.supabase.co
POSTGRES_HOST=db.your-project.supabase.co
POSTGRES_PORT=5432
OLLAMA_BASE_URL=http://localhost:11434
```

### Scenario 3: Full Cloud

Complete cloud deployment.

**Components:**
- Database: Supabase Cloud
- AI Models: Cloud Ollama instance
- API: Container deployment

**Setup:**
```bash
# Configure .env for cloud
SUPABASE_URL=https://your-project.supabase.co
POSTGRES_HOST=db.your-project.supabase.co
OLLAMA_BASE_URL=https://ollama-api.your-domain.com
```

### Scenario 4: Enterprise

Enterprise deployment with dedicated infrastructure.

**Components:**
- Database: Enterprise PostgreSQL cluster
- AI Models: Dedicated GPU cluster
- API: Kubernetes deployment
- Load Balancer: NGINX/HAProxy

**Setup:**
```bash
# Configure .env for enterprise
POSTGRES_HOST=postgres-cluster.internal
POSTGRES_PORT=5432
OLLAMA_BASE_URL=http://ai-cluster.internal:11434
KRAI_API_WORKERS=12
```

## Database Setup

### Local PostgreSQL with Supabase

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize project
supabase start

# Apply schema migrations
supabase db reset
```

### Cloud Database

```bash
# Create Supabase project
# Configure connection in .env
SUPABASE_URL=https://project-id.supabase.co
POSTGRES_HOST=db.project-id.supabase.co
POSTGRES_PORT=5432
```

### Enterprise PostgreSQL

```bash
# Setup PostgreSQL with required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

# Apply KRAI schema
psql -h your-host -p 5432 -U postgres -d krai < database_migrations/init-postgres.sql
```

## AI Models Setup

### Local Ollama Installation

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.2:3b
ollama pull llava:7b
ollama pull embeddinggemma

# Start Ollama service
ollama serve
```

### Cloud Ollama

Configure cloud Ollama endpoint:
```env
OLLAMA_BASE_URL=https://ollama-api.cloud-provider.com
```

### GPU Configuration

#### Apple Silicon (M1/M2/M3)
```env
ML_DEVICE=mps
ML_DEVICE_NAME=Apple_Metal_Performance_Shaders
ML_MEMORY_GB=16
```

#### NVIDIA GPU
```env
ML_DEVICE=cuda
ML_DEVICE_NAME=NVIDIA_RTX_4090
ML_MEMORY_GB=24
```

#### CPU Fallback
```env
ML_DEVICE=cpu
ML_DEVICE_NAME=CPU
ML_MEMORY_GB=8
```

## Docker Deployment

### Single Container

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY backend/ ./
COPY .env ./

RUN pip install -r requirements.txt

EXPOSE 8001
CMD ["python3", "production_main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  krai-api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - POSTGRES_HOST=postgres
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - ollama

  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: krai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  postgres_data:
  ollama_data:
```

## Kubernetes Deployment

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: krai-engine
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: krai-config
  namespace: krai-engine
data:
  .env: |
    POSTGRES_HOST=postgres-service
    OLLAMA_BASE_URL=http://ollama-service:11434
    # ... other config
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: krai-api
  namespace: krai-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: krai-api
  template:
    metadata:
      labels:
        app: krai-api
    spec:
      containers:
      - name: krai-api
        image: krai-engine:latest
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: krai-config
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: krai-api-service
  namespace: krai-engine
spec:
  selector:
    app: krai-api
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
```

## Security Configuration

### API Security
```env
SECRET_KEY=your-256-bit-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

### Database Security
```env
POSTGRES_PASSWORD=secure-random-password
SUPABASE_SERVICE_ROLE_KEY=jwt-service-role-key
```

### SSL/TLS
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout krai-key.pem -out krai-cert.pem

# Configure in .env
SSL_CERT_PATH=/path/to/krai-cert.pem
SSL_KEY_PATH=/path/to/krai-key.pem
```

## Monitoring and Logging

### Application Monitoring
```env
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=9090
```

### Health Checks
```bash
# API Health
curl http://localhost:8001/health

# Model Status
curl http://localhost:8001/api/production/models/status

# Performance Metrics
curl http://localhost:8001/api/production/performance
```

### Log Aggregation
```bash
# Configure log forwarding
LOG_FORMAT=json
LOG_DESTINATION=elasticsearch://logs.your-domain.com:9200
```

## Performance Optimization

### Database Optimization
```sql
-- Create performance indexes
CREATE INDEX CONCURRENTLY idx_documents_manufacturer ON krai_core.documents(manufacturer);
CREATE INDEX CONCURRENTLY idx_chunks_document_id ON krai_intelligence.chunks(document_id);

-- Configure connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
```

### API Optimization
```env
# Worker configuration
KRAI_API_WORKERS=8
ML_CONCURRENT_DOCUMENTS=4
ML_BATCH_SIZE=64
```

### Caching
```env
# Redis caching
REDIS_URL=redis://redis-cluster:6379
CACHE_TTL=3600
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup
pg_dump -h postgres-host -U postgres krai > backup_$(date +%Y%m%d).sql

# Restore
psql -h postgres-host -U postgres -d krai < backup_20240125.sql
```

### Storage Backup
```bash
# Backup Supabase storage
supabase storage cp --recursive supabase://krai-documents ./backup/documents/
supabase storage cp --recursive supabase://krai-images ./backup/images/
```

### Model Backup
```bash
# Backup Ollama models
docker exec ollama-container ollama list
# Export model data
```

## Scaling

### Horizontal Scaling
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: krai-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: krai-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling
```bash
# Read replicas
POSTGRES_READ_HOST=postgres-read-replica
POSTGRES_WRITE_HOST=postgres-master

# Connection pooling
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_POOL_SIZE=20
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database connectivity
telnet postgres-host 5432

# Verify credentials
psql -h postgres-host -U postgres -d krai
```

**Ollama Models Not Found**
```bash
# List available models
ollama list

# Pull missing models
ollama pull llama3.2:3b
```

**API Not Responding**
```bash
# Check process
ps aux | grep production_main.py

# Check logs
tail -f backend/logs/krai.log

# Check port
lsof -i :8001
```

### Log Analysis
```bash
# API errors
grep "ERROR" backend/logs/krai.log

# Performance issues
grep "slow_query" backend/logs/krai.log

# System metrics
curl http://localhost:8001/api/production/performance
```

## Maintenance

### Regular Tasks
1. **Database maintenance**: Weekly vacuum and analyze
2. **Log rotation**: Daily log cleanup
3. **Model updates**: Monthly model refresh
4. **Security updates**: Weekly dependency updates
5. **Performance monitoring**: Daily metrics review

### Update Procedures
```bash
# Update KRAI Engine
git pull origin main
pip install -r requirements.txt --upgrade

# Update models
ollama pull llama3.2:3b
ollama pull llava:7b
ollama pull embeddinggemma

# Database migrations
supabase db reset
```

## Support Contacts

For deployment issues and technical support, contact the development team with:

1. **Environment configuration** (sanitized .env file)
2. **Error logs** (last 100 lines)
3. **System specifications** (CPU, RAM, GPU)
4. **Deployment scenario** (local/cloud/enterprise)

Provide this information for faster resolution of deployment issues.
