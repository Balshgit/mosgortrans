#!/usr/bin/env sh

set -o errexit
set -o nounset

# We are using `gunicorn` for production, see:
# http://docs.gunicorn.org/en/stable/configure.html

# Check that $DJANGO_ENV is set to "production",
# fail otherwise, since it may break things:


# Start gunicorn:
# Docs: http://docs.gunicorn.org/en/stable/settings.html
# Concerning `workers` setting see:
# https://github.com/wemake-services/wemake-django-template/issues/1022
/usr/local/bin/gunicorn server.wsgi \
  --workers 9 \
  --timeout 150 \
  --max-requests 2000 \
  --max-requests-jitter 400 \
  --bind '0.0.0.0:8000' \
  --chdir '/opt/telebot_balsh/telebot' \
  --log-level info \
  --error-logfile "$SHARED_DIR/logs/gunicorn.log" \
  --worker-tmp-dir '/dev/shm' \
  --pid "$SHARED_DIR/logs/gunicorn_pid"
