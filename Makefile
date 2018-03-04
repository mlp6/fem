sphinx-test:
	PYTHONPATH=.. sphinx-build -nT -b dummy docs/ docs/_build/html
test: clean
	py.test -v --cov --pep8

clean:
	find . -name '*.pyc' -exec rm {} +
	find . -name '__pycache__' -exec rm -r {} +

.PHONY: test clean
