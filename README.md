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
- **Reverse proxy**: nginx
- **CI/CD**: GitHub Actions
- **Orchestration**: Kubernetes (minikube for local testing)
- **Infrastructure**: Terraform (deploys to AWS EC2)
- **Monitoring**: Prometheus + Grafana

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

kubectl apply -f k8s/

# check that pods are running
kubectl get pods -n system-info

# open the service in browser
minikube service system-info-service -n system-info
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
│   └── service.yaml
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
