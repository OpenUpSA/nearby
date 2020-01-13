Local
=====

Local is Code for SA's set of Django applications for helping users find
data local to them.

Included apps:

* http://nearby.code4sa.org/councillor/ - find your local ward councillor

Data Sources
------------

This app loads data from the IEC's API (elections.org.za) and supplements
it with data from the Google Sheet at https://docs.google.com/spreadsheets/d/1rtez8t8MGtG7vTQe-wyCrIgsgejwddoshrPkYPECC7E/edit#gid=0

The data from the IEC is cached in a local database cache and is used only
if the IEC server is down.

Local development
-----------------

1. clone the repo
2. ``cd nearby``
2. ``virtualenv --no-site-packages env``
3. ``pip install -r requirements.txt``

You will need to set some environment variables, which are in the Nearby projects folder
on Google Drive. The GOOGLE_SHEETS_API_KEY is big, the simplest way to handle it is to
download it into a local file.

```
export IEC_API_USERNAME=the-username
export IEC_API_PASSWORD=the-password
export GOOGLE_SHEETS_EMAIL=the-email
export GOOGLE_SHEETS_PRIVATE_KEY=`cat google-sheets-key.txt`
```

Then setup the database and run the server:

```
python manage.py createcachetable
python manage.py runserver
```


Production deployment
---------------------

Production deployment assumes you're running on Heroku.

You will need:

* a django secret key
* a cool app name
* Google Sheets API email (see http://gspread.readthedocs.org/en/latest/oauth2.html)
* Google Sheets API private key

```bash
heroku create
heroku addons:add heroku-postgresql
heroku config:set DJANGO_DEBUG=false \
                  DISABLE_COLLECTSTATIC=1 \
                  DJANGO_SECRET_KEY=some-secret-key \
                  IEC_API_USERNAME=the-username \
                  IEC_API_PASSWORD=the-password \
                  GOOGLE_SHEETS_EMAIL=google sheets user email \
                  GOOGLE_SHEETS_PRIVATE_KEY=contents-of-private-key
git push heroku master
```

License
-------

MIT License
