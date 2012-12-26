Focus2 
======

* What is Focus2?

Focus2 is web UI for Altai_. It replaces Focus_ in subsequent versions of Altai. Focus2 is concentrated on developers' tasks only leaving administrative and management tasks for some other piece of software.

Uses Altai API, runs on CentOS 6, written in Python, based on Flask.
License is LGPL v2.1.

* Is it ready?

It is in early alpha but under active development.

* What do I need to use it?

- OpenStack with altai-api service up and running. Altai would do.
- Centos 6 for guaranteed work of Focus2.
- Sufficient disk space required to handle huge file upload of VM images.

* What do I need to write it?

Python and Ruby. See the documentation for details.


* Where are the docs?

Sphinx sources of the documentation is in ./docs/. Prebuild HTML can be found at Altai wiki_

* Where are the tests?

Python testsuite is in ./tests/. Command to run it: python setup.py test
.JavaScript testsuite is in ./jstests/. Commands:
- testacular start config.unit.js
- testacular start config.e2e.js

* Where can I get help?

E-mail: openstack@griddynamics.com
Support Portal: http://griddynamics.zendesk.com/
Issue Tracker: http://altaicloud.myjetbrains.com/
Developers Blog: http://openstackgd.wordpress.com/


_ http://www.griddynamics.com/solutions/altai-private-cloud-for-developers/
_ https://github.com/altai/focus
_ https://altaicloud.atlassian.net/



