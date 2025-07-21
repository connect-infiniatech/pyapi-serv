test:
	curl -X POST http://localhost:8000/test
	@echo "Running tests..."

run:
	python3 src/app.py

# Cleanup resources
clean: 
	@echo "Clean tests..."

.PHONY: run clean test
