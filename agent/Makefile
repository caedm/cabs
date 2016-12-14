SHELL=/bin/bash
SHELLFLAGS="-O extglob -c"
VERSION=$(shell cat ../version.txt)
NAME=cabsagent-windows-$(VERSION)
DIR=build/$(NAME)

default: installer archive

archive:
	mkdir -p $(DIR)
	cd app && cp -r agent_server.pem \
				    broker_cert.pem \
				    cabsagent.conf \
				    cabsagentsvc.exe \
				    install.exe \
		      ../$(DIR)
	mkdir -p $(DIR)/checks
	cd app/checks && cp -r example.bat \
						   pscheck.exe \
						   bad.bat \
				  	 ../../$(DIR)/checks/
	cd build && zip -r $(NAME).zip $(NAME)/

installer:
	makensis app/install.nsi

clean:
	rm -rf build/*
