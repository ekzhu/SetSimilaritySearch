
upload:
	rm -rf ./dist/*
	python setup.py sdist bdist_wheel --universal
	twine upload ./dist/*

install:
	pip install -e .
