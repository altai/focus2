Development
===========


Env Boostrap
------------

You are lucky one if you are developing on Ubuntu because development environment can be boostrapped with script boostrap_dev_ubuntu.sh.

Otherwise it is recommended to follow these steps modifiing them according to your OS specifics:

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


Env Usage
---------

Basically Focus2 is a set of Flask blueprints registered by a minimal Flask application. To add functionality you have to add blueprint. You can create new blueprint and remove existing with rake commands (see `rake -T`).

When you start developing activate your python virtualenv and run `rake hop`. This will start scripts tracking changes in HAML, CoffeeScript and JS files.
After that in another console activate your python virtualenv and run `rake run`. This will install Python package focus2 in development mode (which is very useful if you switch between Git branches) and run development server at port 5000.
If you have settings you want to pass to this development server then edit local_settings.py (see local_settings.py.example).


Few Answers
-----------

- Why do we need Ruby?

Because we use:
 - HAML (to write templates in HAML and have Jinja2 generated)
 - Rake (to organize development tasks).

- Why do we need Node.js?

Because we use:
 - testacular (test runners for JavaScript require it)
 - watchr (to watch changed in files)
 - coffee-script (to write in CoffeeScript)
 - uglify-js (to minify JS)
