# Loan Processing System Makefile
# This file contains common commands for development, testing, and deployment

# Variables
PYTHON = python
MANAGE = $(PYTHON) manage.py
PIP = pip
NPM = npm

# Django commands
.PHONY: runserver
runserver:
	$(MANAGE) runserver

.PHONY: migrate
migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

.PHONY: shell
shell:
	$(MANAGE) shell

# Frontend commands
.PHONY: frontend-install
frontend-install:
	cd frontend && $(NPM) install

.PHONY: frontend-build
frontend-build:
	cd frontend && $(NPM) run build

.PHONY: frontend-dev
frontend-dev:
	cd frontend && $(NPM) start

# Testing commands
.PHONY: test
test:
	$(MANAGE) test

.PHONY: test-coverage
test-coverage:
	coverage run --source='.' $(MANAGE) test
	coverage report

# Email testing
.PHONY: test-email
test-email:
	$(MANAGE) shell < test_email.py

# ML model commands
.PHONY: train-model
train-model:
	$(MANAGE) train_model

# Utility commands
.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} +

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  runserver        - Run Django development server"
	@echo "  migrate          - Run database migrations"
	@echo "  shell            - Run Django shell"
	@echo "  frontend-install - Install frontend dependencies"
	@echo "  frontend-build   - Build frontend for production"
	@echo "  frontend-dev     - Run frontend development server"
	@echo "  test             - Run all tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-email       - Test email functionality"
	@echo "  train-model      - Train ML model"
	@echo "  install          - Install Python dependencies"
	@echo "  clean            - Remove temporary files"