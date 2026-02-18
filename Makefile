.PHONY: help start stop restart logs test deploy-k8s update-k8s k8s-status clean

help:
	@echo ""
	@echo "System Info API — Available Commands"
	@echo "====================================="
	@echo ""
	@echo "  make start       Start local stack (Flask + nginx + monitoring)"
	@echo "  make stop        Stop local stack"
	@echo "  make restart     Restart local stack"
	@echo "  make logs        Follow all container logs"
	@echo "  make test        Run automated tests"
	@echo ""
	@echo "  make deploy-k8s  Deploy/update to minikube"
	@echo "  make update-k8s  Restart pods to pull latest image"
	@echo "  make k8s-status  Show all Kubernetes resources"
	@echo ""
	@echo "  make clean       Remove stopped containers and unused images"
	@echo ""

# Local development
start:
	@echo "Starting local stack..."
	docker-compose up -d
	@echo ""
	@echo "  API:        http://localhost:8080"
	@echo "  Grafana:    http://localhost:3000  (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"
	@echo ""
	@echo "Testing endpoints:"
	@sleep 3
	@curl -s http://localhost:8080/ | head -1 || echo "Waiting for containers..."

stop:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

logs:
	docker-compose logs -f

# Testing
test:
	@echo "Running tests..."
	pip3 install -q -r tests/requirements.txt
	pytest tests/ -v

# Kubernetes
deploy-k8s:
	@echo "Deploying to minikube..."
	kubectl apply -f k8s/
	@echo "Waiting for pods..."
	kubectl wait --for=condition=ready pod \
		-l app=system-info-api \
		-n system-info \
		--timeout=120s
	@echo ""
	@echo "Opening in browser..."
	minikube service system-info-service -n system-info

update-k8s:
	@echo "Restarting pods to pull latest image..."
	kubectl rollout restart deployment/system-info-api -n system-info
	kubectl rollout status deployment/system-info-api -n system-info

k8s-status:
	kubectl get all -n system-info

# Cleanup
clean:
	docker system prune -f
	@echo "Cleaned up stopped containers and dangling images"
