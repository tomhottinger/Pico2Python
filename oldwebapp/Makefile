.PHONY: help build up down restart logs clean setup migrate

help: ## Zeigt diese Hilfe an
	@echo "Verfügbare Befehle:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Führt das Setup-Script aus (migriert von Pico PHP)
	@./setup.sh

build: ## Baut die Docker-Container
	docker-compose build

up: ## Startet die Container
	docker-compose up

up-d: ## Startet die Container im Hintergrund
	docker-compose up -d

down: ## Stoppt die Container
	docker-compose down

restart: ## Startet die Container neu
	docker-compose restart

logs: ## Zeigt die Logs an
	docker-compose logs -f

logs-app: ## Zeigt nur Flask-App Logs
	docker-compose logs -f pico-cms

clean: ## Entfernt Container, Images und Volumes
	docker-compose down -v
	docker system prune -f

dev: ## Startet die App lokal (ohne Docker)
	@echo "Starting Flask in development mode..."
	@export CONFIG_FILE=./volumes/config/config.yml && \
	export CONTENT_DIR=./volumes/content && \
	export THEMES_DIR=./volumes/themes && \
	python app.py

test: ## Testet die Anwendung
	@echo "Testing Flask app..."
	@curl -f http://localhost:5000/ > /dev/null 2>&1 && echo "✅ App is running!" || echo "❌ App is not responding"

migrate: setup build ## Vollständige Migration: Setup + Build
	@echo "Migration abgeschlossen!"

prod: build up-d ## Produktions-Deployment: Build + Start im Hintergrund
	@echo "Production deployment gestartet!"
	@echo "Zugriff: http://localhost"

status: ## Zeigt Container-Status
	docker-compose ps

shell: ## Öffnet eine Shell im App-Container
	docker-compose exec pico-cms /bin/bash

nginx-shell: ## Öffnet eine Shell im Nginx-Container
	docker-compose exec nginx /bin/sh
