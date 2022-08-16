#! /bin/bash


echo "starting the bot"
cd /opt/mosgortrans \
&& source /home/balsh/.cache/pypoetry/virtualenvs/mosgortrans-3eZxMcY3-py3.10/bin/activate \
&& uvicorn app.main:create_app --host localhost --port 8084 --reload --factory