FROM python:3.9.7

ENV PYTHONUNBUFFERED 1

RUN set -ex; \
  apt-get update; \
  # dependencies for building Python packages \
  apt-get install -y build-essential; \
  # psycopg2 dependencies \
  apt-get install -y libpq-dev; \
  # git for codecov file listing \
  apt-get install -y git; \
  # cleaning up unused files \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/lib/apt/lists/*

# Copy, then install requirements before copying rest for a requirements cache layer.
RUN mkdir /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 5000

RUN IEC_API_USERNAME='JUSTFORBUILD' IEC_API_PASSWORD='JUSTFORBUILD' DATABASE_URL='JUSTFORBUILD' GOOGLE_SHEETS_PRIVATE_KEY='JUSTFORBUILD' python manage.py collectstatic --noinput

CMD gunicorn nearby.wsgi:application --log-file - --bind 0.0.0.0:5000