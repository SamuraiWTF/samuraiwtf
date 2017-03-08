#!/bin/bash

# disable the apt-daily service, as it interferes with initialization
systemctl disable apt-daily.service
systemctl disable apt-daily.timer
echo 'Giving systemctl a moment to shut down apt-daily service...'
sleep 10

echo 'Waiting for daily apt process to finish...'
echo 'Be Patient: This may take several minutes!'
pcount=5 #arbitrary number larger than 1
while [ $pcount -gt 1 ]
do
	sleep 5
	pcount=$(ps -ef | grep  -c apt.systemd.daily)
done
echo 'Looks like daily processes is done. Moving on...'

echo 'Running updates...'
ps aux | grep apt
ps aux | grep dpkg
apt-get remove -y --purge libreoffice*
apt-get update
apt-get -y upgrade
# echo 'samurai' | sudo -S apt-get install -y git, python, nikto, w3af-console, w3af, nmap, zenmap, python-pip, apache2, libapache2-mod-php5, mysql-server, libapache2-mod-auth-mysql, php5-mysql, w3af, wireshark, openjdk-7-jre, ruby-full, chromium-browser, firefox, php5-curl, php5-gd
apt-get clean
apt-get autoremove
# These did not work... not sure why?
# debconf-set-selections <<< 'mysql-server mysql-server/root_password samurai'
# debconf-set-selections <<< 'mysql-server mysql-server/root_password_again samurai'
apt-get install -y mysql-server
apt-get install -y git apache2 php php-mysql
mysqladmin -u root password samurai
cp -r /tmp/samuraiwtf/ /