
REPO = yarranyu/yarra-webclient
VERSION ?= latest

build:
	docker build -t $(REPO):$(VERSION) .

run: build
	docker run -rm ${REPO}

push: build
	docker push  $(REPO):$(VERSION)

test:
	parallel -j0 --lb ::: 'celery worker --app=webclient.app.celery --concurrency=1 --loglevel=INFO' 'cd webclient && flask run'

default: build
