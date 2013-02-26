FOCUS2_SETTINGS := $(PWD)/etc/local_settings.py

FIRST: run


test:
	FOCUS2_SETTINGS=$(FOCUS2_SETTINGS) python setup.py test


run:
	python setup.py develop
	FOCUS2_SETTINGS=$(FOCUS2_SETTINGS) python -m focus2.runserver


js-unit:
	(cd jstests && testacular start config.unit.js)


js-e2e:
	(cd jstests && testacular start config.e2e.js)
