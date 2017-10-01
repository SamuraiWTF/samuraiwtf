#!/bin/bash

sudo docker run --rm -p 3000:3000 bkimminich/juice-shop &

cd /opt/targets/dojo-basic-docker
sudo docker-compose up &

sudo service nginx restart;curl http://dojo-basic.wtf/reset-db.php
