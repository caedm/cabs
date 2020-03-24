all:
	mkdir -p build
	cp rgsconnect.py build
	cp CABS_client.conf build
	cp cert.pem build
	cp postextraction.sh build
	makeself --nox11 --nowait ./build rgsconnect_installer.sh "RGS Connect" ./postextraction.sh
	rm -rf build
