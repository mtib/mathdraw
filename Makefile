build: draw.py pgf.py
	rm -rf build dist *.spec || :;
	cxfreeze draw.py

run: build
	./dist/draw

deps:
	pip3 install -r requirements.txt
