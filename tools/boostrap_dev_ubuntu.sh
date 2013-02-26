#!/bin/bash
sudo apt-get update
sudo apt-get install build-essential curl wget git-core libssl-dev

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
cd ../

sudo easy_install virtualenv virtualenvwrapper
echo '. /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv Focus2
workon Focus2
easy_install pip
pip install -r dev_requirements.pip
python setup.py develop
deactivate
