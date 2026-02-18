# System Info API — DevOps Portfolio Project

![CI](https://github.com/alex2frisky/system-info-api/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/alex2frisky/system-info-api/actions/workflows/cd.yml/badge.svg)

A production-grade DevOps pipeline built around a simple Flask API that returns system information. The application itself is intentionally simple — **the focus is entirely on the DevOps infrastructure surrounding it**.

Built as a portfolio project demonstrating real-world DevOps practices: containerization, CI/CD automation, container orchestration, infrastructure as code, and complete observability.

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
│  Docker Image: username/system-info-api:latest                 │
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

## 🚀 Quick Start (Local)

### Prerequisites

- Docker Desktop
- Python 3.11+
- Git

### Run Locally

```bash
# Clone the repository
git clone git@github.com:alex2frisky/system-info-api.git
cd system-info-api

# Start everything (Flask + nginx + Prometheus + Grafana)
docker-compose up -d

# Wait 30 seconds for all services to start

# Test the API
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/info
curl http://localhost:8080/metrics

# Access services
# API:        http://localhost:8080
# Grafana:    http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### View Live Dashboards

Open Grafana at `http://localhost:3000` (admin/admin) to see:
- Real-time nginx request rate
- System CPU, memory, and disk usage
- Flask request counter
- Connection states

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information and endpoint list |
| `/health` | GET | Health check (Kubernetes probes use this) |
| `/info` | GET | Detailed system information (CPU, memory, disk, uptime) |
| `/metrics` | GET | Prometheus metrics in text exposition format |

### Example Response

```bash
$ curl http://localhost:8080/info
```

```json
{
  "hostname": "abc123",
  "platform": {
    "system": "Linux",
    "machine": "x86_64"
  },
  "cpu": {
    "count": 8,
    "percent": 15.2,
    "per_cpu": [12.1, 14.3, 18.2, 16.5, 13.7, 15.8, 14.2, 17.1]
  },
  "memory": {
    "total_gb": 16.0,
    "used_gb": 8.5,
    "available_gb": 7.5,
    "percent": 53.1
  },
  "disk": {
    "total_gb": 500.0,
    "used_gb": 250.0,
    "free_gb": 250.0,
    "percent": 50.0
  },
  "uptime": {
    "boot_time": "2024-01-15T10:30:00",
    "uptime_seconds": 86400,
    "uptime_hours": 24.0
  },
  "timestamp": "2024-01-16T10:30:00"
}
```

---

## ☸️ Deploy to Kubernetes (minikube)

### Prerequisites

- minikube installed
- kubectl installed

### Deploy

```bash
# Start minikube
minikube start --driver=docker

# Deploy to Kubernetes
kubectl apply -f k8s/

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  -l app=system-info-api \
  -n system-info \
  --timeout=120s

# Access the service
minikube service system-info-service -n system-info
# Opens browser automatically
```

### Update Deployment

```bash
# After pushing a new image to Docker Hub
kubectl rollout restart deployment/system-info-api -n system-info
kubectl rollout status deployment/system-info-api -n system-info
```

### Demonstrate Self-Healing

```bash
# Delete a pod
kubectl delete pod $(kubectl get pods -n system-info -o name | head -1) -n system-info

# Watch Kubernetes create a replacement immediately
kubectl get pods -n system-info --watch
```

---

## 🏗️ Deploy to AWS

### Prerequisites

- AWS CLI configured (`aws configure`)
- Terraform installed

### Deploy

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Create infrastructure
terraform apply
# Type: yes

# Wait 3-5 minutes for EC2 to boot and start Docker

# Get the public IP
terraform output public_ip

# Test
curl http://$(terraform output -raw public_ip)/info
```

### Destroy (IMPORTANT!)

```bash
# Always destroy when done to avoid charges
terraform destroy
# Type: yes
```

**Cost:** ~$0.017/hour (~$0.40/day if you forget to destroy)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Expected: 12 tests pass
```

---

## 📈 Monitoring

The project includes a complete observability stack:

**Prometheus** collects metrics from:
- nginx (via nginx-prometheus-exporter)
- Flask application `/metrics` endpoint

**Grafana** visualizes:
- nginx request rate and active connections
- System CPU, memory, and disk usage (from Flask)
- Flask request counter
- Connection states

The Grafana dashboard is **provisioned as code** — stored in `grafana/provisioning/dashboards/system-info.json` and automatically loaded on startup.

---

## 🔄 CI/CD Pipeline

### Continuous Integration (`ci.yml`)

**Triggers:** Every push to any branch

**Steps:**
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run pytest test suite
5. Verify Docker build succeeds

If any step fails → ❌ GitHub shows red X, blocks merge

### Continuous Deployment (`cd.yml`)

**Triggers:** Push to `main` branch only (after CI passes)

**Steps:**
1. Checkout code
2. Set up Docker Buildx
3. Login to Docker Hub
4. Build for both `linux/amd64` and `linux/arm64`
5. Tag with `latest` and `sha-{commit}`
6. Push to Docker Hub

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
├── grafana/
│   └── provisioning/               # Dashboards as code
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           ├── dashboards.yml
│           └── system-info.json    # Grafana dashboard JSON
│
├── tests/
│   ├── test_api.py                 # Flask endpoint tests
│   └── requirements.txt            # Test dependencies
│
├── .github/workflows/
│   ├── ci.yml                      # Test + build verification
│   └── cd.yml                      # Build + push to Docker Hub
│
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── nginx-config.yaml
│   ├── deployment.yaml             # 2 replicas (Flask + nginx sidecar)
│   └── service.yaml
│
├── terraform/
│   ├── main.tf                     # AWS infrastructure
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars            # Your values (gitignored)
│
├── scripts/                        # Helper scripts
├── Makefile                        # Unified commands
├── .gitignore
├── .dockerignore
└── README.md                       # This file
```

---

## 💡 Key DevOps Concepts Demonstrated

### Containerization
- Multi-stage Docker builds (builder + runtime)
- Non-root user in containers
- Health checks built into images
- Multi-architecture support (arm64 + amd64)

### CI/CD
- Automated testing on every commit
- Security through branch protection
- Immutable artifacts (sha-tagged images)
- Separation of CI (test) and CD (deploy)

### Kubernetes
- Deployment with replica management
- Liveness and readiness probes
- Resource requests and limits
- ConfigMap for configuration
- Sidecar pattern (nginx alongside Flask)
- LoadBalancer service
- Rolling updates with zero downtime

### Infrastructure as Code
- Complete AWS environment defined in Terraform
- Reproducible infrastructure
- Version-controlled infrastructure changes
- State management

### Observability
- Metrics collection (Prometheus)
- Visualization (Grafana)
- Dashboards as code (stored in Git)
- Application metrics + infrastructure metrics
- Multi-source monitoring (nginx + Flask)

---

## 🎯 Why This Project Structure

### Simple Application, Complex Infrastructure

The Flask application is intentionally simple (120 lines). It returns system information — no database, no complex business logic, no authentication.

**Why?**

Because this is a **DevOps project**, not a backend project. The complexity and learning are in:
- How the app is containerized
- How it's tested automatically
- How it's deployed consistently
- How it's monitored in production
- How the infrastructure is managed

When debugging, 90% of issues will be DevOps issues (Docker, K8s, networking, configuration) rather than application bugs. That's intentional.

### Production-Grade Practices

- **Grafana dashboards as code** — most tutorials tell you to click in the UI
- **Health checks everywhere** — Docker, K8s liveness/readiness, EC2 user data verification
- **Multi-stage Docker builds** — smaller final images
- **Non-root containers** — security best practice
- **Resource limits** — prevents resource starvation
- **Separation of concerns** — Flask generates data, nginx serves it, Prometheus collects it
- **Sidecar pattern in K8s** — nginx and Flask in same pod

---

## 📝 Interview Talking Points

### "Why Flask instead of a static site?"

> "A static site would work, but Flask lets me demonstrate a few additional concepts: application health endpoints that Kubernetes probes can use, custom Prometheus metrics from the application itself, and the sidecar pattern with nginx as a reverse proxy. It's still simple enough that 90% of my time was spent on DevOps, not debugging the app."

### "Why the sidecar pattern in Kubernetes?"

> "In the Kubernetes deployment, Flask and nginx run in the same pod as separate containers. This demonstrates the sidecar pattern — nginx handles TLS termination, request buffering, and static asset caching, while Flask focuses purely on generating dynamic responses. It's a common production pattern."

### "Why both local and AWS?"

> "minikube is for development and demonstrating Kubernetes features live in interviews — self-healing, rolling updates, scaling. AWS deployment via Terraform shows I can translate that to real cloud infrastructure. Both use the same Docker image, showing true environment consistency."

### "What would you add for production?"

> "For real production: HTTPS with a proper certificate, horizontal pod autoscaling based on actual traffic patterns, a production Kubernetes cluster instead of minikube, centralized logging with something like ELK or Loki, distributed tracing, and likely a database for storing historical system stats. But those additions would triple the complexity for diminishing portfolio value."

---

## 🧑‍💼 About

**Built by:** [Your Name]  
**Background:** 10 years in production support → DevOps engineer  
**GitHub:** [github.com/alex2frisky](https://github.com/alex2frisky)  
**LinkedIn:** [linkedin.com/in/YOUR-PROFILE](https://linkedin.com/in/YOUR-PROFILE)

This project was built to demonstrate production-grade DevOps practices. The system information API serves as a simple, reliable payload — the real value is in the automation, monitoring, and infrastructure surrounding it.

---

## 📄 License

MIT License — feel free to use this project structure for your own portfolio.
