
REPO = yarranyu/webclient-nginx
VERSION ?= latest

build:
	docker build -t $(REPO):$(VERSION) .

run: build
	docker run ${REPO}

push: build
	docker push  $(REPO):$(VERSION)
