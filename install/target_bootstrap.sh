#! /bin/bash

##################################################################
# SAMURAI TARGET SERVER
##################################################################

echo 'Bootstrapping Samurai Target Server...'

echo 'Installing Docker Community Edition...'

echo "deb http://ftp.debian.org/debian jessie-backports main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update

sudo apt-get install -y vim

sudo apt-get install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common

echo "...getting key..."
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "...got key, adding docker repo..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
echo "...updating apt cache..."
sudo apt-get update
echo "...installing docker-ce..."
sudo apt-get install -y docker-ce
echo "...Docker CE installed."

echo 'Installing Docker Compose...'
sudo curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
#The above curl throws a bunch of output into stderr when working fine. Consider redirecting somewhere else.
sudo chmod +x /usr/local/bin/docker-compose
echo '...Docker Compose installed.'

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