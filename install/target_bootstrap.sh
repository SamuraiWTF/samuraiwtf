#! /bin/bash

##################################################################
# SAMURAI TARGET SERVER
##################################################################

echo 'Bootstrapping Samurai Target Server...'

echo 'Installing Docker Community Edition...'

echo "deb http://ftp.debian.org/debian jessie-backports main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update

sudo apt-get install vim

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

#DOJO SCAVENGER

#MUTILLIDAE

echo 'Installing nginx'
sudo apt-get install -y nginx

echo 'Setting up reverse-proxy config'
sudo cp /tmp/config/sites-enabled/* /etc/nginx/sites-enabled/

echo 'All finished!'