VERSION=$(shell cat ../version.txt)
NAME=cabsagent-$(VERSION)
DIR=build/$(NAME)

all: archive

archive:
	mkdir -p $(DIR)
	cp -r app/* $(DIR)
	cd $(DIR)/..
	tar -czvf $(DIR).tar.gz $(DIR)

clean:
	rm -rf build/*
