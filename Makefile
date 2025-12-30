PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= asia-northeast1
IMAGE_NAME = aozora-importer
REPO_NAME = aozora
IMAGE_TAG = latest
ARTIFACT_REGISTRY = $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/importer

.PHONY: build run submit

# Build the Docker image locally
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Run the Docker container locally
# Mounts credentials if GOOGLE_APPLICATION_CREDENTIALS is set
run:
run:
	docker run --rm \
		-e GOOGLE_CLOUD_PROJECT=$(PROJECT_ID) \
		-e AOZORA_CSV_URL=$(AOZORA_CSV_URL) \
		-v ~/.config/gcloud:/root/.config/gcloud \
		$(IMAGE_NAME):$(IMAGE_TAG)

# Submit the build to Cloud Build
submit:
	gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=$(REGION),COMMIT_SHA=$$(git rev-parse --short HEAD) .
