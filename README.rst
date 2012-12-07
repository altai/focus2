======
Focus2 
======

is web-based UI for Altai. It is concentrated on developers' tasks.
Uses Altai API, runs on CentOS 6, written in Python, based on Flask.

Install
=======

Development
===========

Prerequisites
-------------

Get yourself a *nix system (Ubuntu would do) with Python (2.5 or higher).

Environment Setup
-----------------

At Ubuntu run boostrap_dev_ubuntu.sh or perform actions manually.
Code examples below are valid for Ubuntu 12.04.

.. code:: bash
 # 1. install some tools
 sudo apt-get install build-essential curl wget git-core

 # 2. install setuptools if required
 http://peak.telecommunity.com/dist/ez_setup.py
 sudo python ez_setup.py 

 # 2. install virtualenv and virtualenvwrapper(recommended)
 sudo easy_install virtualenv virtualenvwrapper
 . /usr/local/bin/virtualenvwrapper.sh
 echo '. /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc

 # 3. initiate Python virtualenv
 mkvirtualenv Focus2
 workon Focus2
 
 # 4. install Python  dependencies
 easy_install pip
 pip install -r install_requirements.txt
 pip install -r dev_requirements.txt

 # 5. install the package in development mode
 cd focus2
 python setup.py develop
 cd ../
  
 # 6. install RVM
 bash -s stable < <(curl -s https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer)
 echo '[[ -s "~/.rvm/scripts/rvm" ]] && . "~/.rvm/scripts/rvm"' >> ~/.bashrc
 source ~/.rvm/scripts/rvm

 # 7. install Ruby
 rvm install ruby-1.9.3
 rvm use --default 1.9.3

 # 8. install Ruby dependencies
 gem install bundler
 bundle install

Process
-------

Whenever you want to add new features generate new blueprint with command `rake bp`. You'll be asked few questions. New blueprint will appear in directory focus2.blueprints. Edit it to implement required features.


License
=======

LGPL v2.1, the copy is in file COPYING
