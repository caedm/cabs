VERSION=$(shell cat ../version.txt)
RGSVERSION=7.3.1.10284-1
NAME=rgsconnect-$(OS)-$(VERSION)
DIR=build/$(NAME)

GEN=build/pyinstaller
DIST=$(GEN)/dist
OPTS=--onefile --clean --distpath $(DIST) --workpath $(GEN) \
     --specpath $(GEN) --name RGSConnect-$(DISTRO)

RPM=app/src/rgreceiver_linux_64-$(RGSVERSION).x86_64.rpm
DEB=app/src/rgreceiver-linux-64_$(RGSVERSION)_amd64.deb

all: linux windows

linux: ubuntu rhel archive

archive: $(RPM) $(DEB)
	$(eval OS := linux)
	mkdir -p $(DIR)
	cp -rL app/* $(DIR)
	cp $(DIST)/RGSConnect-ubuntu $(DIR)/src/
	cp $(DIST)/RGSConnect-rhel $(DIR)/src/
	cp ../version.txt $(DIR)/src/version.txt
	rm $(DIR)/src/CABS_client.py
	tar -C build -cvf $(DIR).tar.gz $(NAME)/

ubuntu:
	$(eval DISTRO := ubuntu)
	mkdir -p $(GEN)
	docker build -t clientubuntu -f ./extra/Dockerfile-ubuntu ./extra
	docker run --rm -v $(CURDIR):/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientubuntu \
	    pyinstaller $(OPTS) app/src/CABS_client.py

$(DEB): $(RPM)
	docker build -t clientubuntu -f ./extra/Dockerfile-ubuntu ./extra
	docker run --rm -v $(CURDIR)/app/src/:/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientubuntu \
	    fakeroot alien -k --scripts $(shell basename $(RPM))

rhel:
	$(eval DISTRO := rhel)
	mkdir -p $(GEN)
	docker build -t clientrhel -f ./extra/Dockerfile-rhel ./extra
	docker run --rm -v $(CURDIR):/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientrhel \
	    pyinstaller $(OPTS) app/src/CABS_client.py

windows: $(DIST)/RGSConnect-windows.exe
	$(eval OS := windows)
	mkdir -p $(DIR)
	cp $(DIST)/RGSConnect-windows.exe $(DIR)/RGSConnect.exe
	cd app/src && cp cert.pem \
					 Header.png \
					 Icon.png \
					 icon.ico \
				  ../../$(DIR)/
	cd extra && cp ReceiverSetup.exe \
				   mkinstaller.nsi \
				../$(DIR)/
	cp extra/CABS_client-windows.conf $(DIR)/CABS_client.conf
	cp ../version.txt $(DIR)/version.txt
	cd $(DIR) && makensis -DVERSION=$(VERSION) mkinstaller.nsi
	rm $(DIR)/mkinstaller.nsi
	cd build && zip -r $(NAME).zip $(NAME)

clean:
	rm -rf build/*

test:
	$(eval DISTRO := ubuntu)
	mkdir -p $(GEN)
	docker build -t clientubuntu -f ./extra/Dockerfile-ubuntu ./extra
	docker run --rm -it -v $(CURDIR):/tmp/code -w /tmp/code \
		--user $(shell id -u):$(shell id -g) clientubuntu \
		bash
