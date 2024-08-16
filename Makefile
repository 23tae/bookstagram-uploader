IMAGE_NAME = bookstagram-uploader
CONTAINER_NAME = book-uploader

.PHONY: build run stop clean rebuild restart all

build:
	@if [ -z "$$(docker images -q $(IMAGE_NAME))" ]; then \
		echo "Building Docker image..."; \
		docker build -t $(IMAGE_NAME) .; \
	else \
		echo "Docker image $(IMAGE_NAME) already exists. Skipping build."; \
	fi

run: build
	@if [ -z "$$(docker ps -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "Running Docker container..."; \
		docker run -d -p 5001:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME); \
	else \
		echo "Docker container $(CONTAINER_NAME) is already running."; \
	fi

stop:
	@if [ ! -z "$$(docker ps -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "Stopping Docker container..."; \
		docker stop $(CONTAINER_NAME); \
	else \
		echo "No running container named $(CONTAINER_NAME) to stop."; \
	fi

clean:
	@if [ ! -z "$$(docker ps -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "Stopping and removing Docker container..."; \
		docker stop $(CONTAINER_NAME); \
		docker rm $(CONTAINER_NAME); \
	else \
		echo "No running container named $(CONTAINER_NAME) to stop."; \
	fi
	@if [ ! -z "$$(docker images -q $(IMAGE_NAME))" ]; then \
		echo "Removing Docker image..."; \
		docker rmi $(IMAGE_NAME); \
	else \
		echo "No image named $(IMAGE_NAME) to remove."; \
	fi

rebuild: stop build run

restart:
	@if [ ! -z "$$(docker ps -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "Restarting Docker container..."; \
		docker stop $(CONTAINER_NAME); \
		docker start $(CONTAINER_NAME); \
	else \
		echo "No running container named $(CONTAINER_NAME) to restart."; \
	fi

all: build run
