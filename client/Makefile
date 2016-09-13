VERSION=$(shell cat ../version.txt)
NAME=rgsconnect_linux-$(VERSION)
BIN=RGSConnect

SRC=src/CABS_client.py
FILES=res/{RGSConnect.conf,cert.pem,Header.png,Icon.png,install.sh} \
	  res/rgreceiver*.{deb,rpm}
GEN=build/pyinstaller
OPTS=--onefile --distpath $(GEN)/dist --workpath $(GEN) --specpath $(GEN) \
	 --name $(BIN)
DIR=build/$(NAME)

all: deps bin archive

archive: $(GEN)/dist/$(BIN)
	mkdir -p $(DIR)
	cp $(GEN)/dist/$(BIN) $(FILES) $(DIR)
	cd $(DIR)/..
	tar -cvf $(DIR).tar.gz $(DIR)
	
$(GEN)/dist/$(BIN): bin

bin:
	mkdir -p $(GEN)
	pyinstaller $(OPTS) $(SRC)
	
deps:
	pip install -r requirements.txt

clean:
	rm -rf build/*

foo:
	echo $(VERSION)
