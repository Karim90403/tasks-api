# file gunicorn.conf.py
# coding=utf-8


import multiprocessing

from core.gunicorn_config import GunicornConfig

conf = GunicornConfig()

loglevel = conf.log_level
errorlog = "-"
accesslog = "-"

bind = conf.gunicorn_bind_url

workers = multiprocessing.cpu_count() * 2 + 1

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

worker_class = "uvicorn.workers.UvicornWorker"
