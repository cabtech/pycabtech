lint: .pylint

.pylint: setup.py pycabtech/*.py
	flake8 --ignore=E501 $^
	black $^
	pylint $^
	@touch .pylint

sdist: .pylint
	python setup.py sdist

clean:
	@/bin/rm  -f .pylint
	@/bin/rm -rf build dist *.egg-info
