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
rm -rf "static/"


python manage.py migrate

python manage.py shell << EOF
from bambu.models import Folder  # Adjust the import to match your app's structure

Folder.objects.create(name="default")
EOF

python manage.py shell << EOF
from bambu.models import PredefinedCommand  # Adjust the import to match your app's structure

PredefinedCommand.objects.create(name="Start Print", command="M24", description="Start the print job")
PredefinedCommand.objects.create(name="Pause Print", command="M25", description="Pause the current print job")
PredefinedCommand.objects.create(name="Stop Print", command="M108", description="Stop the print job")
EOF

export DJANGO_SUPERUSER_PASSWORD="hc"
python manage.py createsuperuser --noinput --username hc --email hc@hc.local


python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages
python manage.py collectstatic
