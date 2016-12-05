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
					checks/ \
		      ../$(DIR)
	cd build && zip -r $(NAME).zip $(NAME)/

installer:
	makensis app/install.nsi

clean:
	rm -rf build/*
