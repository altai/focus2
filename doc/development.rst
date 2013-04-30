Development
===========

Up and running:

1. Run Altai API
 a. ask aababilov or apugachev for Virtualbox VM with Altai and Altai API installed OR
    - install Altai according to instructions https://altaicloud.atlassian.net/wiki/display/V110/Installation 
    - clone Altai API from https://github.com/altai/altai-api
    - upload working directory content to the Altai master node into /root
    - create altai-api/local_settings.py like::
PRETTY_PRINT_JSON=True
KEYSTONE_URI='http://localhost:5000/v2.0'
ALTAI_API_SUPERUSER = 'aname'
ALTAI_API_SUPERUSER_PASSWORD = 'apass'
USE_RELOADER=False
SQLALCHEMY_DATABASE_URI='sqlite:////root/altai.db'
MAIL_USERNAME = "someone@someone.com"
MAIL_PASSWORD = "apass"
DEFAULT_MAIL_SENDER = ('robot', "someone@someone.com")
 
      ALTAI_API_SUPERUSER and ALTAI_API_SUPERUSER_PASSWORD come from 
      /opt/altai/altai-node.json entries (created during Altai install)::
   "admin-login-name": "...",
   ...
   "admin-login-password": "...",

  b. in /root/ run::
ALTAI_API_SETTINGS=/root/altai-api/local_settings.py tools/run.py

2. Run Focus
 a. get ubuntu
 b. clone focus2 repo from https://github.com/altai/focus2
 c. install mysql, create database focus2, grant all for focus2 with password focus2
 d. in working directory create etc/local_settings.py like::
API_ENDPOINT = 'http://altai_master:5039'
APP_TEMP_DIR = '/tmp'
DB_HOST = 'localhost'
DB_NAME = 'focus2'
DB_USER = 'focus2'
DB_PASSWD = 'focus2'
INVITATION_DOMAINS = ['griddynamics.com', 'gmail.com']
USE_RELOADER = True
DEBUG = True
BILLING_URL = 'http://altai_master:8787/v2/'

    altai_master is hostname for Altai master node (for VM with Altai take a look at ifconfig inside the VM)
  e. create a Python virtual environment and activate it (mkvirtualenv focus2 if you use virtualenvwrapper)
  e. run make, it will install python dependencies
  f. open http://0.0.0.0:8282/ in a browser
  g. use credentials for ALTAI_API_SUPERUSER from Altai API if you are clueless about user credentials at this point.
