CONTAINER_NAME = coursework_mod006203_st_server
IMAGE_NAME = coursework_mod006203_st_image

build:
	docker compose build

up:
	make build
	docker compose -f docker-compose.yml --project-name ${CONTAINER_NAME} up -d --force-recreate

down:
	docker kill ${CONTAINER_NAME}
	docker rm ${CONTAINER_NAME}

cleanup:
	make prune
	docker image rm ${IMAGE_NAME}

prune:
	make down
	docker container prune
	docker image prune
	docker network prune
