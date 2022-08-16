#! /bin/bash


echo "starting the bot"
cd /opt/mosgortrans \
&& source /home/balsh/.cache/pypoetry/virtualenvs/mosgortrans-3eZxMcY3-py3.10/bin/activate \
&& gunicorn app.main:create_app --bind prod-server.lan:8084 --worker-class aiohttp.GunicornWebWorker