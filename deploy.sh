#!/usr/bin/sh
cd $(dirname $0)/
git pull
python manage.py synkdb
sudo python manage.py collectstatic
sudo /etc/init.d/apache2 reload
