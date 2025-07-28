.PHONY: install setup test lint format clean run migrate

# Install dependencies
install:
	pip install -r requirements.txt

# Setup development environment
setup: install
	cp env.example .env
	@echo "Please edit .env file with your Supabase credentials"

# Run tests
test:
	python run_tests.py

# Run linting only
lint:
	black src/ tests/ --check
	isort src/ tests/ --check-only
	flake8 src/ tests/

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

# Run development server
run:
	python start.py

# Run migrations
migrate:
	alembic upgrade head

# Create new migration
migration:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

# Show help
help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies"
	@echo "  setup     - Setup development environment"
	@echo "  test      - Run tests with coverage"
	@echo "  lint      - Run code linting"
	@echo "  format    - Format code with black and isort"
	@echo "  clean     - Clean up cache files"
	@echo "  run       - Start development server"
	@echo "  migrate   - Run database migrations"
	@echo "  migration - Create new migration"
	@echo "  help      - Show this help" 