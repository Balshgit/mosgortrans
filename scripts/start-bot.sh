#! /bin/bash

echo "starting the bot"

gunicorn main:create_app \
  --bind 0.0.0.0:8084 \
  --worker-class aiohttp.GunicornWebWorker \
  --timeout 150 \
  --max-requests 2000 \
  --max-requests-jitter 400
