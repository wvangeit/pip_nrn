clean:
	rm -rf dist
	rm -rf nrn.egg-info
twine: clean
	python setup.py sdist
	pip install twine
	twine upload --skip-existing dist/*
install: clean
	pip -v install . --upgrade	
