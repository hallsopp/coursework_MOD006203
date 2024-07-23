CONTAINER_NAME = coursework_mod006203_st_server
BASH_CONTAINER_NAME = coursework_mod006203_st_bash
IMAGE_NAME = coursework_mod006203_st_image

build:
	docker compose build

up:
	make build
	docker compose up -d project_docker --force-recreate

bash:
	make build
	docker compose run --rm project_docker_bash

down:
	docker kill ${CONTAINER_NAME} || true
	docker rm ${CONTAINER_NAME} || true
	docker kill ${BASH_CONTAINER_NAME} || true
	docker rm ${BASH_CONTAINER_NAME} || true

cleanup:
	make prune
	docker image rm ${IMAGE_NAME}

prune:
	make down
	docker system prune -a -f
