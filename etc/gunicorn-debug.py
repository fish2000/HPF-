bind = "127.0.0.1:8000"
pidfile = "/Users/fish/Praxa/HPF/var/run/gunicorn.pid"

worker_class = 'eventlet'

workers = 1
timeout = 666
max_requests = 333

preload_app = False
debug = True

