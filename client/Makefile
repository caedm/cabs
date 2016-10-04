VERSION=$(shell cat ../version.txt)
NAME=rgsconnect_linux-$(VERSION)

GEN=build/pyinstaller
OPTS=--onefile --clean --distpath $(GEN)/dist --workpath $(GEN) \
     --specpath $(GEN) --name RGSConnect-$(PLATFORM)

all: ubuntu rhel archive

archive:
	mkdir -p build/$(NAME)
	cp -r app/* build/$(NAME)
	cp $(GEN)/dist/RGSConnect-ubuntu build/$(NAME)/src/
	cp $(GEN)/dist/RGSConnect-rhel build/$(NAME)/src/
	rm build/$(NAME)/src/CABS_client.py
	tar -C build -cvf build/$(NAME).tar.gz $(NAME)/

ubuntu:
	$(eval PLATFORM := ubuntu)
	mkdir -p $(GEN)
	docker build -t clientubuntu -f ./extra/Dockerfile-ubuntu ./extra
	docker run --rm -v ${CURDIR}:/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientubuntu \
	    pyinstaller $(OPTS) app/src/CABS_client.py

rhel:
	$(eval PLATFORM := rhel)
	mkdir -p $(GEN)
	docker build -t clientrhel -f ./extra/Dockerfile-rhel ./extra
	docker run --rm -v ${CURDIR}:/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientrhel \
	    pyinstaller $(OPTS) app/src/CABS_client.py

clean:
	rm -rf build/*
