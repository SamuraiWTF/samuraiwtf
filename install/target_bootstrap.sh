#! /bin/bash

##################################################################
# SAMURAI TARGET SERVER
##################################################################

echo 'Bootstrapping Samurai Target Server...'

echo 'Constructing target apps...'
sudo mkdir /opt/targets

echo 'Setting up Juice Shop app...'
sudo docker pull bkimminich/juice-shop
#sudo docker run -d -p 3000:3000 bkimminich/juice-shop

#BWAPP

#DOJO BASIC
echo 'Setting up dojo-basic...'
echo '...cloning repo...'
sudo git clone --recursive https://github.com/mgillam/dojo-basic-docker.git /opt/targets/dojo-basic-docker
echo '...rewriting db config...'
sudo rm /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "<?php" | sudo tee /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "\$dbhost = 'db';" | sudo tee -a /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "\$dbuser = 'root';" | sudo tee -a /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "\$dbpass = 'dojo';" | sudo tee -a /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "\$dbname = 'dojo_basic';" | sudo tee -a /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo "?>" | sudo tee -a /opt/targets/dojo-basic-docker/app/dojo-basic/config.inc
echo '...initializing services...'
cd /opt/targets/dojo-basic-docker
echo '...starting app...'
sudo docker-compose up -d
echo '...calling db init php script...'
curl http://localhost:30080/reset-db.php #currently doesn't work. Might need a dependson directive in the compose yml
echo '...stopping app...'
sudo docker-compose down
echo 'Done.'

#DOJO SCAVENGER

#MUTILLIDAE

#Reverse Proxy

echo 'Installing nginx'
sudo apt-get install -y nginx

echo 'Setting up reverse-proxy config'
sudo cp /tmp/config/sites-enabled/* /etc/nginx/sites-enabled/

#Update hosts entries
#TODO

echo 'All finished!'
