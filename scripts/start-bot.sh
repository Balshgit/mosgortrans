#! /bin/bash


echo "starting the bot"
cd /opt/mosgortrans \
&& source /home/balsh/.cache/pypoetry/virtualenvs/mosgortrans-3eZxMcY3-py3.10/bin/activate \
&& gunicorn app.main:create_app \
  --bind prod-server.lan:8084 \
  --worker-class aiohttp.GunicornWebWorker \
  --timeout 150 \
  --max-requests 2000 \
  --max-requests-jitter 400 \
  --chdir "/opt/mosgortrans/logs" \
  --log-level info \
  --error-logfile "/opt/mosgortrans/logs/gunicorn_err.log" \
  --worker-tmp-dir "/tmp" \
  --pid "/opt/mosgortrans/logs/gunicorn_pid"