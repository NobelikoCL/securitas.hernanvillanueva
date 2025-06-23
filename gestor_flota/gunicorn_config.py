"""Gunicorn configuration file."""

# Django WSGI application path
wsgi_app = "gestor_flota.wsgi:application"

# The number of worker processes for handling requests
workers = 4

# The socket to bind
bind = "0.0.0.0:8000"

# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

# Redirect stdout/stderr to specified file in errorlog
capture_output = True

# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn/prod.pid"

# Daemonize the Gunicorn process (detach & run in the background)
daemon = True
