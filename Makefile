PY_TARGET_DIRS=app # settings tests
PY_TARGET_FILES=

PORT=8000

.PHONY: app
app:
	poetry run python app/main.py

# standard commands to run on every commit
format:
	autoflake --recursive --ignore-init-module-imports --remove-all-unused-imports --remove-unused-variables --in-place $(PY_TARGET_DIRS)
	pyupgrade --keep-runtime-typing $(PY_TARGET_FILES)
	isort --color --quiet $(PY_TARGET_DIRS)
	black $(PY_TARGET_DIRS) -S

check-style:
	black --check $(PY_TARGET_DIRS) -S --diff --color

check-imports:
	isort --check-only $(PY_TARGET_DIRS)

lint-typing:
	mypy $(PY_TARGET_DIRS)

lint-complexity:
	flake8 $(PY_TARGET_DIRS)

# special commands
lint-deps:
	safety check --full-report

# docker commands
test-deps-up:
	docker compose -f tests/docker-compose.yml up -d

test-deps-down:
	docker compose -f tests/docker-compose.yml down -v
