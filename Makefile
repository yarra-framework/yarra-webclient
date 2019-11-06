
REPO = yarra-webclient
VERSION ?= latest

build:
	docker build -t $(REPO):$(VERSION) .

run: build
	docker run ${REPO}

test:
	parallel -j0 --lb ::: 'celery worker --app=src.app.celery --concurrency=1 --loglevel=INFO' 'flask run'

default: build
