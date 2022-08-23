#! /bin/bash

echo "starting the bot"

gunicorn main:create_app \
  --bind 127.0.0.1:8084 \
  --worker-class aiohttp.GunicornWebWorker \
  --timeout 150 \
  --max-requests 2000 \
  --max-requests-jitter 400 \
  --chdir "/app/logs" \
  --log-level info \
  --error-logfile "/app/logs/gunicorn_err.log" \
  --worker-tmp-dir "/tmp" \
  --pid "/app/logs/gunicorn_pid"