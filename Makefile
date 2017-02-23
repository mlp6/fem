test: clean
	py.test -v --cov

clean:
	find . -name '*.pyc' -exec rm {} +
	find . -name '__pycache__' -exec rm -r {} +

.PHONY: test clean
