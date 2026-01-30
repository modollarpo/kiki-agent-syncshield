# Proto generation
.PHONY: proto
proto:
	@echo "Generating protos in shared/proto..."
	cd shared/proto && \
	for f in *.proto; do \
	  protoc --proto_path=. --go_out=gen --go-grpc_out=gen $$f; \
	done
	@echo "Generating protos in services/syncshield/safefail..."
	cd ../../services/syncshield/safefail && \
	protoc --proto_path=. --go_out=. --go-grpc_out=. safefail.proto
	@echo "Generating protos in schemas..."
	cd ../../../schemas && \
	protoc --proto_path=. --go_out=. --go-grpc_out=. explainability_notification.proto
	@echo "Proto generation complete."
# KIKI Agent™ Makefile

.PHONY: all build test lint up down logs deploy clean

all: build test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs --tail=100 -f

test:
	cd services/syncbrain && pytest
	cd services/syncvalue && pytest
	cd services/synccreate && pytest
	cd services/syncengage && pytest
	cd api-gateway && pytest
	cd services/syncshield/app && go test ../tests -v
	cd services/syncflow && go test ./tests -v

lint:
	cd services/syncbrain && flake8 app
	cd services/syncvalue && flake8 app
	cd services/synccreate && flake8 app
	cd services/syncengage && flake8 app
	cd api-gateway && flake8 app
	cd services/syncshield/app && golint .
	cd services/syncflow && golint ./app

clean:
	docker-compose down -v
	docker system prune -f

# Kubernetes deploy (requires kubectl & helm)
deploy:
	kubectl apply -f deploy/k8s/
