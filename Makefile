test: clean
	py.test -v --cov --pep8

clean:
	find . -name '*.pyc' -exec rm {} +
	find . -name '__pycache__' -exec rm -r {} +

.PHONY: test clean
