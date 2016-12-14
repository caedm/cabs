SHELL=/bin/bash
SHELLFLAGS="-O extglob -c"
VERSION=$(shell cat ../version.txt)
NAME=cabsagent-$(OS)-$(VERSION)
DIR=build/$(NAME)

default: windows linux

windows: installer winconf archive

linux: linconf archive

linconf:
	$(eval OS := linux)
	$(eval APPFILES := agent_server.pem broker_cert.pem \
			cabsagent.py cabsagent.service install.sh \
			requirements.txt)
	$(eval CHECKFILES := pscheck.py nopanel.py example.py bad.sh)

winconf:
	$(eval OS := windows)
	$(eval APPFILES := agent_server.pem broker_cert.pem \
			cabsagentsvc.exe install.exe)
	$(eval CHECKFILES := example.bat pscheck.exe bad.py)


archive:
	mkdir -p $(DIR)
	cd app && cp -r $(APPFILES) ../$(DIR)
	cp app/cabsagent-$(OS).conf $(DIR)/cabsagent.conf
	mkdir -p $(DIR)/checks
	cd app/checks && cp -r $(CHECKFILES) ../../$(DIR)/checks/
	echo $(VERSION) > $(DIR)/version.txt
	cd build && zip -r $(NAME).zip $(NAME)/

installer:
	makensis app/install.nsi

clean:
	rm -rf build/*
