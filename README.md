ozp-v3
=====================
Django-based prototype for new OZP backend

## Getting Started
First, install python. You probably want to use a virtualenv, but it's not
required. This is known to work with Python 3.3+, and should work with Python
2.7.6+ as well.

With Python installed (and optionally using a virtualenv), install the
dependencies: `pip install -r requirements.txt`

Now run the server: `./restart_clean_dev_server.sh`

Take a look at the browsable api at `http://localhost:8000/api/`. Use
username `wsmith` password `password` when promted for authentication info

There's also the admin interface at `http://localhost:8000/admin`
(username: `admin`, password: `password`)