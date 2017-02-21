build: draw.py server.py
	rm -rf build dist *.spec || :;
	cxfreeze draw.py --target-dir=dist/draw
	cxfreeze server.py --target-dir=dist/serve
	echo 'MATHDRAW=$$1 ./draw' > dist/draw/mathdraw.sh
	chmod +x dist/draw/mathdraw.sh

run: build
	./dist/draw/draw

serve: build
	./dist/serve/server

deps:
	pip3 install -r requirements.txt
