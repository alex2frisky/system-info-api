# System Info API

![CI](https://github.com/alex2frisky/system-info-api/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/alex2frisky/system-info-api/actions/workflows/cd.yml/badge.svg)

A Flask-based REST API that provides real-time system information (CPU, memory, disk usage) with complete DevOps automation: containerization, CI/CD, Kubernetes orchestration, infrastructure as code, and monitoring.

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB                                  │
│                                                                 │
│  Code Push  →  GitHub Actions CI  →  Tests + Build            │
│                       ↓                                         │
│                  GitHub Actions CD  →  Build + Push to Docker Hub │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DOCKER HUB                                 │
│                                                                 │
│  Docker Image: alex2frisky/system-info-api:latest                 │
│                (multi-arch: amd64 + arm64)                      │
└─────────────────────────────────────────────────────────────────┘
           ↓                                    ↓
┌──────────────────────────────┐  ┌────────────────────────────────┐
│    LOCAL (minikube)          │  │     AWS (Terraform)            │
│                              │  │                                │
│  Kubernetes Cluster          │  │  VPC + EC2 + Security Groups   │
│  ├── 2 Pods (Flask + nginx)  │  │  ├── Docker on EC2             │
│  ├── LoadBalancer Service    │  │  ├── Elastic IP                │
│  └── ConfigMaps              │  │  └── Flask container           │
│                              │  │                                │
│  Monitoring Stack:           │  │  Access: http://EC2_IP         │
│  ├── Prometheus              │  │                                │
│  ├── Grafana                 │  │                                │
│  └── nginx-exporter          │  │                                │
└──────────────────────────────┘  └────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Application** | Python, Flask, gunicorn |
| **Containerization** | Docker (multi-arch: arm64, amd64) |
| **Reverse Proxy** | nginx |
| **CI/CD** | GitHub Actions |
| **Testing** | pytest |
| **Orchestration** | Kubernetes (minikube local, production-ready manifests) |
| **Infrastructure** | Terraform |
| **Cloud** | AWS (VPC, EC2, Security Groups, Elastic IP) |
| **Monitoring** | Prometheus, Grafana, nginx-prometheus-exporter |
| **Version Control** | Git, GitHub |

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Python 3.11+
- Git

### Run Locally

```bash
# Clone the repository
git clone https://github.com/alex2frisky/system-info-api.git
cd system-info-api

# Start the full stack (Flask + nginx + Prometheus + Grafana)
docker-compose up -d

# Wait 30 seconds for all services to start

# Test the API
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/info
curl http://localhost:8080/metrics
```

**Access the services:**
- API: http://localhost:8080
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information and endpoint list |
| `/health` | GET | Health check (used by Kubernetes probes) |
| `/info` | GET | Detailed system information (CPU, memory, disk, uptime) |
| `/metrics` | GET | Prometheus metrics in text exposition format |

---

## ☸️ Kubernetes Deployment

### Deploy to minikube

```bash
# Start minikube
minikube start --driver=docker

# Deploy application
kubectl apply -f k8s/

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  -l app=system-info-api \
  -n system-info \
  --timeout=120s

# Access the service
minikube service system-info-service -n system-info
```

### Update Deployment

```bash
# Restart pods to pull latest image
kubectl rollout restart deployment/system-info-api -n system-info
kubectl rollout status deployment/system-info-api -n system-info
```

---

## 🏗️ AWS Deployment

### Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Create infrastructure
terraform apply

# Wait 3-5 minutes for EC2 to boot and start Docker
# Test the deployment
curl http://$(terraform output -raw public_ip)/info
```

### Destroy Infrastructure

```bash
# Always destroy when done to avoid AWS charges
terraform destroy
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v
```

All tests validate:
- API endpoint responses
- Health check functionality
- System data accuracy
- Prometheus metrics format
- Request counter functionality

---

## 📈 Monitoring

### Prometheus

Collects metrics from:
- nginx (via nginx-prometheus-exporter)
- Flask application (`/metrics` endpoint)

Access at: http://localhost:9090

### Grafana

Pre-configured dashboards showing:
- nginx request rate and active connections
- System CPU, memory, and disk usage
- Flask request counter
- Connection states

Access at: http://localhost:3000 (admin/admin)

**Dashboard provisioning:** The Grafana dashboard is stored as code in `grafana/provisioning/dashboards/system-info.json` and automatically loaded on startup.

---

## 🔄 CI/CD Pipeline

### Continuous Integration (`ci.yml`)

**Triggers:** Every push to any branch

**Steps:**
1. Run pytest test suite
2. Verify Docker build succeeds

### Continuous Deployment (`cd.yml`)

**Triggers:** Push to `main` branch (after CI passes)

**Steps:**
1. Build Docker image for `linux/amd64` and `linux/arm64`
2. Tag with `latest` and `sha-{commit}`
3. Push to Docker Hub

---

## 💡 Key Features

### Application Design

- Simple Flask API focused on system information
- No database or complex business logic
- Production-ready patterns: health checks, metrics, logging

### DevOps Infrastructure

- **Containerization**: Multi-stage Docker builds, non-root containers
- **CI/CD**: Automated testing and deployment on every commit
- **Orchestration**: Kubernetes with 2 replicas, health probes, resource limits
- **Infrastructure as Code**: Complete AWS environment in Terraform
- **Monitoring**: Prometheus + Grafana with dashboards as code
- **Multi-architecture**: Supports both arm64 (Mac M series) and amd64 (servers)

### Production Patterns

- Grafana dashboards provisioned from Git
- Sidecar pattern (nginx + Flask in same pod)
- Health checks at every level (Docker, Kubernetes, AWS)
- Resource limits to prevent resource contention
- Rolling updates for zero-downtime deployments
- Immutable infrastructure (destroy and recreate identically)

---

## 📁 Project Structure

```
system-info-api/
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── nginx.conf                      # nginx reverse proxy config
├── docker-compose.yml              # Full local stack
├── prometheus.yml                  # Prometheus scrape config
│
├── grafana/provisioning/           # Dashboards as code
│   ├── datasources/
│   │   └── prometheus.yml
│   └── dashboards/
│       ├── dashboards.yml
│       └── system-info.json
│
├── tests/                          # Automated tests
│   ├── test_api.py
│   └── requirements.txt
│
├── .github/workflows/              # CI/CD pipelines
│   ├── ci.yml
│   └── cd.yml
│
├── k8s/                            # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── nginx-config.yaml
│   ├── deployment.yaml
│   └── service.yaml
│
├── terraform/                      # AWS infrastructure
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
│
└── README.md
```


**Built by:** Alex B
**GitHub:** [@alex2frisky](https://github.com/alex2frisky)  
**LinkedIn:** [linkedin.com/in/alexbazilescu](https://linkedin.com/in/alexbazilescu)
