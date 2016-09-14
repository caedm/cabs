VERSION=$(shell cat ../version.txt)
NAME=cabsbroker-$(VERSION)

FILES=src/cabsbroker.py \
	  res/{cabsbroker.service,install.sh,setupDatabase.py} \
	  res/{cabsbroker.conf,requirements.txt,createdb.sql}
DIR=build/$(NAME)

all: archive

archive:
	mkdir -p $(DIR)
	cp $(FILES) $(DIR)
	cd $(DIR)/..
	tar -cvf $(DIR).tar.gz $(DIR)

clean:
	rm -rf build/*
