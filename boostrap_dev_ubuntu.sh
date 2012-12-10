#!/bin/bash
sudo apt-get update
sudo apt-get install build-essential curl wget git-core libssl-dev

git clone git://github.com/creationix/nvm.git ~/.nvm
echo '. ~/.nvm/nvm.sh' >> ~/.bashrc
. ~/.nvm/nvm.sh
nvm install v0.8
nvm alias default 0.8
cd jstests
npm install -g
ln -s /usr/bin/chromium-browser google-chrome
ln -s /usr/bin/firefox firefox
cd ../

bash -s stable < <(curl -s https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer)
echo '\n[[ -s "~/.rvm/scripts/rvm" ]] && . "~/.rvm/scripts/rvm"' >> ~/.bashrc
. ~/.rvm/scripts/rvm
rvm install ruby-1.9.3
rvm use 1.9.3
gem install bundler
bundle install

sudo easy_install virtualenv virtualenvwrapper
echo '\n. /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv Focus2
workon Focus2
easy_install pip
pip install -r dev_requirements.pip
python setup.py develop
deactivate
