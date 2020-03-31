all:
	mkdir -p build
	cp rgsconnect.py build
	cp rgsconnect_legacy.py build
	cp CABS_client.conf build
	cp cert.pem build
	cp postextraction.sh build
	cp rgs.sh build
	makeself --nox11 --nowait --needroot ./build rgsconnect_installer.sh "RGS Connect" ./postextraction.sh
	rm -rf build
