container_runtime := $(shell which podman || which docker)

$(info using ${container_runtime})

up:
	${container_runtime} compose up --build -d

down:
	${container_runtime} compose down

clean:
	${container_runtime} compose down -v

migrations:
	${container_runtime} compose run --rm backend uv run python manage.py makemigrations


