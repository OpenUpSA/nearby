Local
=====

Local is Code for SA's set of Django applications for helping users find
data local to them.

Included apps:

* http://local.code4sa.org/councillor/ - find your local ward councillor

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
