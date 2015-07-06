Ward Councillor
===============

Small Django application to help users find information on their local
ward councillor based on their address, browser location or ID number.

Production deployment
---------------------

Production deployment assumes you're running on Heroku.

You will need:

* a django secret key
* a New Relic license key
* a cool app name

```bash
heroku create
heroku addons:add heroku-postgresql
heroku config:set DJANGO_DEBUG=false \
                  DISABLE_COLLECTSTATIC=1 \
                  DJANGO_SECRET_KEY=some-secret-key \
                  NEW_RELIC_APP_NAME=cool app name \
                  NEW_RELIC_LICENSE_KEY=new relic license key
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

License
-------

MIT License
