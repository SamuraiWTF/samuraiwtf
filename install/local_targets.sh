#!/bin/bash

echo 'Setting hosts entries for local targets'

echo '127.0.0.1   juice-shop.wtf' | sudo tee -a /etc/hosts
echo '127.0.0.1   dojo-basic.wtf' | sudo tee -a /etc/hosts

sudo run --rm -p 3000:3000 bkimminich/juice-shop &

cd /opt/targets/dojo-basic
sudo docker-compose up &

sudo service nginx restart;curl http://dojo-basic.wtf/reset-db.php
