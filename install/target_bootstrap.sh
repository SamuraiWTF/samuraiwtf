#! /bin/bash

##################################################################
# SAMURAI TARGET SERVER
##################################################################

echo 'Bootstrapping Samurai Target Server...'

echo 'Constructing target apps...'
sudo mkdir /opt/targets

echo 'Setting up Juice Shop app...'
export JUICE_LINK=https://github.com$(curl -L -s https://github.com/bkimminich/juice-shop/releases/latest | grep node8_linux_x64.tgz | grep href | cut -d '"' -f 2)
curl -s -L $JUICE_LINK -o /tmp/juiceshop.tgz
tar xvfz /tmp/juiceshop.tgz -C /opt/targets 

#sudo docker pull bkimminich/juice-shop
#sudo docker run -d -p 3000:3000 bkimminich/juice-shop:snapshot
echo 'Pulling DVWA docker image...'
sudo docker pull bit0pus/docker-dvwa

#MUTILLIDAE
echo 'Pulling Mutillidae docker image...'
sudo docker pull bit0pus/docker-mutillidae

#BWAPP

#DOJO BASIC
echo 'Setting up Samurai Dojo...'
echo '...cloning repo...'
sudo git clone --recursive https://github.com/SamuraiWTF/samurai-dojo-docker.git /opt/targets/samurai-dojo-docker
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
sudo tr '\r\n' '\n' < /tmp/config/init_db.sh > /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger/init_db.sh
sudo chmod 755 /opt/targets/samurai-dojo-docker/apps/Samurai-Dojo/scavenger/init_db.sh
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

#Reverse Proxy

echo 'Installing nginx'
sudo apt-get install -y nginx php-fpm

echo 'Setting up reverse-proxy config'
pushd /tmp/config/sites-enabled
for f in ./*
do
	sudo tr '\r\n' '\n' < "$f" > "/etc/nginx/sites-enabled/$f"
done
popd

# Setting up default nginx site with vulnscripts (this is a temporary fix - ideally vulnscripts should be a separate docker target)
echo 'setting up vulnscripts on localhost'
pushd /var/www/html
sudo mkdir vulnscripts
cd vulnscripts/
sudo tar xf /tmp/config/www/html/vulnscripts.tar
popd

# Setting up professionallyevil.wtf
echo 'setting up professionallyevil.wtf'
pushd /var/www
sudo mkdir professionallyevil
sudo chown samurai:samurai professionallyevil
cd professionallyevil
sudo echo 'It Works ;)' > index.html
sudo chown samurai:samurai index.html
popd

# Setting up amoksecurity.wtf
echo 'setting up amoksecurity.wtf'
pushd /var/www
sudo mkdir amoksecurity
sudo chown samurai:samurai amoksecurity
cd amoksecurity
sudo echo 'It Works ;)' > index.html
sudo chown samurai:samurai index.html
popd


#Update hosts entries
#TODO

echo 'All finished!'
