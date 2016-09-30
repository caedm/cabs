VERSION=$(shell cat ../version.txt)
NAME=rgsconnect_linux-$(VERSION)

GEN=build/pyinstaller
OPTS=--onefile --distpath $(GEN)/dist --workpath $(GEN) --specpath $(GEN) \
	 --name RGSConnect

all: deps bin archive

archive:
	mkdir -p build/$(NAME)
	cp -r app/* build/$(NAME)
	#cp build/dist/* build/$(NAME)/src/
	#rm build/$(NAME)/src/CABS_client.py
	tar -C build -cvf build/$(NAME).tar.gz $(NAME)/

$(GEN)/dist/RGSConnect: bin

bin:
	mkdir -p $(GEN)
	#pyinstaller $(OPTS) app/src/CABS_client.py
	cxfreeze app/src/CABS_client.py --target-dir build/dist

deps:
	pip install -r requirements.txt

clean:
	rm -rf build/*
