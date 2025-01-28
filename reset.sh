#!/bin/bash
rm db.sqlite3

for d in */
do
  module=`realpath $d --relative-to=.`
  echo "clearing $module"
  if [ -d $d/__pycache__ ] ;
  then
    rm -rf $d/__pycache__
  fi

  if [ -d $d/migrations ] ;
  then
    rm -rf $d/migrations/*
    python manage.py makemigrations $module
  fi

done

rm -f "gcode/*"
rm -f "threemf/*"
rm -rf "media/*"

python manage.py migrate
export DJANGO_SUPERUSER_PASSWORD="hc"
python manage.py createsuperuser --noinput --username hc --email hc@hc.local


python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages

