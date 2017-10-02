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
echo 'Setting up Samurai Dojo...'
echo '...cloning repo...'
sudo git clone --recursive https://github.com/mgillam/samurai-dojo-docker.git /opt/targets/samurai-dojo-docker
echo '...rewriting db config...'
sudo rm /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "<?php" | sudo tee /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "\$dbhost = 'basicdb';" | sudo tee -a /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "\$dbuser = 'root';" | sudo tee -a /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "\$dbpass = 'samurai';" | sudo tee -a /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "\$dbname = 'samurai_dojo_basic';" | sudo tee -a /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo "?>" | sudo tee -a /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/config.inc
echo '...initializing services...'
cd /opt/targets/samurai-dojo-docker
sudo rm /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/basic/.htaccess
sed "s/localhost/scavengerdb/g" /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger/partners.php | sudo tee /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger/partners.php
sudo cp /tmp/config/init_db.sh /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger
echo '...starting app...'
sudo docker-compose up -d
sleep 15
echo '...calling db init php script...'
cd /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger
sudo bash init_db.sh
cd /opt/targets/samurai-dojo-docker
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
