FIRST: run


test:
	python setup.py test


run:
	python setup.py develop
	FOCUS2=$(PWD)/etc/local_settings.py python -m focus2.runserver


js-unit:
	(cd jstests && testacular start config.unit.js)


js-e2e:
	(cd jstests && testacular start config.e2e.js)
