FOCUS2_SETTINGS := $(PWD)/etc/local_settings.py

FIRST: run


test:
	FOCUS2_SETTINGS=$(FOCUS2_SETTINGS) python setup.py test


run:
	pip install -U 'distribute>=0.6.28'
	python setup.py develop
	FOCUS2_SETTINGS=$(FOCUS2_SETTINGS) python -m focus2.runserver


js-unit:
	(cd jstests && testacular start config.unit.js)


js-e2e:
	(cd jstests && testacular start config.e2e.js)


clean:
	find . -name '*.pyc' -exec $(RM) {} \;


nvm:
	git clone git://github.com/creationix/nvm.git ~/.nvm
	echo '. ~/.nvm/nvm.sh' >> ~/.bashrc
	. ~/.nvm/nvm.sh
	nvm install v0.8
	nvm alias default 0.8
	npm install
	npm install testacular -g
	cd jstests
	ln -s /usr/bin/chromium-browser google-chrome
	ln -s /usr/bin/firefox firefox


install-deps:
	apt-get install build-essential curl wget git libssl-dev libmysqlclient-dev virtualenvwrapper
