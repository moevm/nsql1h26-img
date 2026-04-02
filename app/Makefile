container_runtime := $(shell which podman || which docker)
backend_folder := ./backend/

$(info using ${container_runtime})

up:
	${container_runtime} compose up --build -d

down:
	${container_runtime} compose down

clean:
	${container_runtime} compose down -v

migrations-docker:
	${container_runtime} compose run --rm backend uv run python manage.py makemigrations


migrations-local:
	 cd ${backend_folder} && MONGO_HOST=localhost uv run python manage.py makemigrations

lint-install:
	cd ${backend_folder} && uv run pre-commit install --config .pre-commit-config.yaml

lint:
	cd ${backend_folder} && uv run pre-commit run --files $(git ls-files 'app/**')
