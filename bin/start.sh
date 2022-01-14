#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python manage.py collectstatic --noinput
gunicorn --worker-class gevent nearby.wsgi:application --log-file -
