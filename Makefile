# Wake up docker containers
up:
	docker-compose -f docker-compose.yml up -d

# Shut down docker containers
down:
	docker-compose -f docker-compose.yml down

# Show a status of each container
status:
	docker-compose -f docker-compose.yml ps

# Status alias
s: status

# Show logs of each container
logs:
	docker-compose -f docker-compose.yml logs

# Restart all containers
restart: down up

# Build and up docker containers
build:
	docker-compose -f docker-compose.yml build --force-rm

# Build and up docker containers
rebuild: down build

connect:
	 docker exec -it vpn-manager bash

grant-permissions:
	docker-compose -f docker-compose.yml exec -T -u root vpn-manager-postgres chown postgres:postgres /var/lib/postgresql/data

lint:
	@echo "Start checking ruff..."
	docker run -it --volume=./src:/src --rm  registry.atb-it.ru/linters/python-lints/ruff:stable ruff --config=/pyproject.toml /src
	@echo "Stop checking ruff..."

refactor:
	@echo "Start checking ruff..."
	docker run -it --volume=./src:/src --rm  registry.atb-it.ru/linters/python-lints/ruff:stable ruff --fix --config=/pyproject.toml /src
	@echo "Stop checking ruff..."

force-refactor:
	@echo "Start checking ruff..."
	docker run -it --volume=./src:/src --rm registry.atb-it.ru/linters/python-lints/ruff:stable ruff --unsafe-fixes --fix --config=/pyproject.toml /src
	@echo "Stop checking ruff..."
