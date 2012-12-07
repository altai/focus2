#!/bin/bash
sudo apt-get update
sudo apt-get install build-essential curl wget git-core

bash -s stable < <(curl -s https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer)
echo '[[ -s "~/.rvm/scripts/rvm" ]] && . "~/.rvm/scripts/rvm"' >> ~/.bashrc
. ~/.rvm/scripts/rvm
rvm install ruby-1.9.3
rvm use 1.9.3
gem install bundler
bundle install

sudo easy_install virtualenv virtualenvwrapper
echo '. /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv Focus2
easy_install pip
pip install -r install_requirements.pip
pip install -r dev_requirements.pip
cd focus2
python setup.py develop
cd ../
deactivate
