# System Info API

![CI](https://github.com/alex2frisky/system-info-api/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/alex2frisky/system-info-api/actions/workflows/cd.yml/badge.svg)

Flask REST API that exposes real-time system metrics (CPU, memory, disk) with a full DevOps stack: Docker, Kubernetes, Terraform, GitHub Actions, Prometheus, and Grafana.

---

## What it does

The app has four endpoints:

| Endpoint | Description |
|----------|-------------|
| `/` | basic service info |
| `/health` | health check (used by K8s probes) |
| `/info` | CPU, memory, disk, uptime |
| `/metrics` | Prometheus metrics |

---

## Stack

- **App**: Python + Flask + gunicorn
- **Container**: Docker
- **Reverse proxy**: nginx (Docker Compose) / nginx Ingress Controller (Kubernetes)
- **CI/CD**: GitHub Actions
- **Orchestration**: Kubernetes (minikube for local testing)
- **Infrastructure**: Terraform (deploys to AWS EC2)
- **Monitoring**: Prometheus + Grafana

---

## Architecture

```
CI/CD PIPELINE
-----------------------------------------------------------------
  Developer
      |
      | git push
      v
  GitHub (alex2frisky/system-info-api)
      |
      |-- any branch --> [ CI ]  lint + test + docker build
      |
      +-- main --------> [ CD ]  build multi-arch image
                               |
                               | docker push :latest
                               v
                         Docker Hub
                  (alex2frisky/system-info-api:latest)


DOCKER COMPOSE  (local dev + monitoring)
-----------------------------------------------------------------
  Browser / curl
       |  localhost:8080
       v
  [ nginx ]  reverse proxy
       |  proxy_pass :5000
       v
  [ Flask + gunicorn ]
       |  scrapes /metrics every 15s
       v
  [ Prometheus ] -------> [ Grafana ]
    :9090                   :3000


KUBERNETES  (minikube)
-----------------------------------------------------------------
  curl / browser
       |
       v
  [ nginx Ingress Controller ]  (minikube addon)
       |
       v
  [ ClusterIP Service ]  :80 -> :5000
       |
    +--+--+
    |     |
    v     v
  [Pod 1] [Pod 2]  Deployment (replicas: 2)
  [     ConfigMap: FLASK_ENV=production    ]


AWS  (Terraform)
-----------------------------------------------------------------
  terraform apply
       |
       v
  VPC + Public Subnet + Internet Gateway + Security Group
       |
       v
  EC2  (Amazon Linux 2, t2.micro)
  user_data: installs Docker, pulls image, starts container
       |
       v
  [ alex2frisky/system-info-api:latest ]
       |
       v
  Elastic IP  (stable public address)
```

---

## How it works

1. **Push to GitHub.** The CI pipeline runs on every branch — lints with flake8, runs pytest, and verifies the Docker build. Nothing merges broken.

2. **Merge to main triggers CD.** GitHub Actions builds a multi-architecture image (amd64 + arm64) and pushes it to Docker Hub as `:latest`. That single image is what both Kubernetes and AWS pull from.

3. **Local dev uses Docker Compose.** `docker compose up` starts four containers: nginx (reverse proxy on port 8080), Flask + gunicorn, Prometheus (scrapes `/metrics`), and Grafana (dashboards). Good for testing the full stack locally without Kubernetes.

4. **Kubernetes runs two replicas behind an Ingress.** The nginx Ingress Controller (a minikube addon) is the single entry point. It routes traffic to the ClusterIP Service, which load-balances across the two Flask pods. Liveness and readiness probes both hit `/health` so Kubernetes knows when a pod is ready and when to restart it.

5. **AWS is fully automated with Terraform.** `terraform apply` creates the VPC, subnet, internet gateway, security group, EC2 instance, and Elastic IP in one go. The instance bootstraps itself via a `user_data` script — it installs Docker and starts the container on first boot, no manual SSH needed.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11+
- For Kubernetes: `kubectl` + `minikube`
- For AWS: `terraform` + AWS CLI configured (`aws configure`)

---

## Run locally with Docker Compose

This starts the Flask app, nginx, Prometheus, and Grafana together.

```bash
git clone https://github.com/alex2frisky/system-info-api.git
cd system-info-api

make up
# or: docker-compose up -d
```

- API: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## Kubernetes (minikube)

```bash
minikube start --driver=docker

# enable the nginx ingress controller (only needed once)
minikube addons enable ingress

kubectl apply -f k8s/

# check pods and ingress are ready
kubectl get pods -n system-info
kubectl get ingress -n system-info
```

Access the API via the minikube node IP:
```bash
curl http://$(minikube ip)/info
```

Or run `minikube tunnel` in a separate terminal (keeps running), then use localhost:
```bash
# terminal 1
minikube tunnel

# terminal 2
curl http://localhost/info
```

To restart after pushing a new image:
```bash
kubectl rollout restart deployment/system-info-api -n system-info
```

---

## AWS with Terraform

This creates a VPC, EC2 instance, and Elastic IP, then runs the Docker container on boot.

```bash
cd terraform

# update terraform.tfvars with your Docker Hub image and SSH key path

terraform init
terraform plan
terraform apply
```

Wait ~3-5 minutes for EC2 to boot and pull the image, then:
```bash
curl http://$(terraform output -raw public_ip)/health

# SSH in to check logs or debug
ssh ec2-user@$(terraform output -raw public_ip)
sudo cat /var/log/user-data.log
```

Always destroy when done:
```bash
terraform destroy
```

---

## CI/CD

- **CI** (`ci.yml`): runs on every push — lints with flake8, runs tests, verifies Docker build
- **CD** (`cd.yml`): runs on push to main — builds and pushes image to Docker Hub

Needs `DOCKER_USERNAME` and `DOCKER_PASSWORD` set in GitHub secrets.

---

## Tests

```bash
pip install -r tests/requirements.txt
make test
# or: pytest tests/ -v
# .venv/bin/pytest tests/ -v
```

---

## Project structure

```
system-info-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── Makefile
├── nginx.conf
├── docker-compose.yml
├── prometheus.yml
├── grafana/provisioning/
│   ├── datasources/prometheus.yml
│   └── dashboards/
│       ├── dashboards.yml
│       └── system-info.json
├── tests/
│   ├── test_api.py
│   └── requirements.txt
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── k8s/
│   ├── 00-namespace.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── terraform.tfvars
```

---

**Built by:** Alex B
**GitHub:** [@alex2frisky](https://github.com/alex2frisky)
**LinkedIn:** [linkedin.com/in/alexbazilescu](https://linkedin.com/in/alexbazilescu)
