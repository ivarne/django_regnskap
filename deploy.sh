#!/usr/bin/sh
cd $(dirname $0)/
git pull
python manage.py syncdb
sudo python manage.py collectstatic
sudo /etc/init.d/apache2 reload
