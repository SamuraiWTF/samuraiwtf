#!/bin/bash

sudo docker run --rm -p 3000:3000 bkimminich/juice-shop &

sudo docker run --rm -p 31000:80 -p 33006:3306 bit0pus/docker-dvwa &

sudo docker run --rm -p 33080:80 -p 22222:22 -p 33333:3306 bit0pus/docker-mutillidae &

cd /opt/targets/samurai-dojo-docker
sudo docker-compose up &

sudo service nginx restart;curl http://dojo-basic.wtf/reset-db.php
