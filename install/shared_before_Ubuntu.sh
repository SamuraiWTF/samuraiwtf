#!/bin/bash
#Modified from the orriginal to work with Ubuntu
#echo 'Adding stretch-backports'

#echo "deb http://ftp.debian.org/debian stretch-backports main" | sudo tee -a /etc/apt/sources.list
#sudo apt-get update

echo 'Installing Docker Community Edition...'


sudo apt-get install -y vim

sudo apt-get install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     software-properties-common

echo "...getting key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo "...got key, adding docker repo..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
echo "...updating apt cache..."
sudo apt-get update
echo "...installing docker-ce..."
sudo apt-get install -y docker-ce
echo "...Docker CE installed."

echo 'Installing Docker Compose...'
sudo curl -sSL https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
#The above curl throws a bunch of output into stderr when working fine. Consider redirecting somewhere else.
sudo chmod +x /usr/local/bin/docker-compose
echo '...Docker Compose installed.'
