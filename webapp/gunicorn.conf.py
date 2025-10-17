# Gunicorn Konfiguration für Pico CMS

bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "pico-cms"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None
