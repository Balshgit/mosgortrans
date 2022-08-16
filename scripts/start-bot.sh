#! /bin/bash


echo "starting the bot"
cd /opt/mosgortrans \
&& source /home/balsh/.cache/pypoetry/virtualenvs/mosgortrans-3eZxMcY3-py3.10/bin/activate \
&& gunicorn app.main:create_app --bind localhost:8084 --reload --worker-class aiohttp.GunicornWebWorker