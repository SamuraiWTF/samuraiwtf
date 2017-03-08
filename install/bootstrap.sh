#! /bin/bash

##################################################################
# SYSTEM
##################################################################

echo 'Bootstraping SamuraiWTF...'
export DEBIAN_FRONTEND=noninteractive

hostname samuraiwtf

# Disable the apt-daily service, as it interferes with initialization
systemctl disable apt-daily.service
systemctl disable apt-daily.timer

# These next few are in case the apt-daily service has already started
echo 'Waiting for daily apt process to finish...'
echo 'Be Patient: This may take several minutes!'
pcount=$(ps -ef | grep  -c apt.systemd.daily)
while [ $pcount -gt 1 ]
do
	sleep 5
	pcount=$(ps -ef | grep  -c apt.systemd.daily)
done

echo 'Running updates...'
apt-get update
apt-get -y upgrade
if [ ! -d /opt/samurai ]; then
	echo 'Removing unecessary default packages...'
	apt-get remove -y --purge libreoffice*
	apt-get -y clean
	apt-get -y autoremove
else
	echo 'Skipping removal of default packages'
fi

echo 'Installing AMP stack...'
# These next two did not work... not sure why?
# debconf-set-selections <<< 'mysql-server mysql-server/root_password samurai'
# debconf-set-selections <<< 'mysql-server mysql-server/root_password_again samurai'

if [ -d /etc/mysql/mysql.conf.d ]; then
	apt-get install -y mysql-server	
else
	apt-get install -y mysql-server
	mysqladmin -u root password samurai
fi
apt-get install -y git apache2 php php-mysql libapache2-mod-php

echo 'Copying directories...'
cp -r /tmp/samuraiwtf/etc/* /etc/
cp -r /tmp/samuraiwtf/opt/* /opt/
cp -r /tmp/samuraiwtf/usr/* /usr/
cp -r /tmp/samuraiwtf/var/* /var/

echo 'Checking if samurai user has been added...'
# Add the samurai user if we don't have it, and add to the sudo group
USERCOUNT=`cat /etc/passwd |grep "samurai:" | wc -l`
if [ $USERCOUNT -eq 0 ]; then
  echo "It looks like the samurai user does not exist.  Adding..."
  useradd -d /home/samurai -U -m -s /bin/bash -G sudo -p b.jPTlW8tPfR6 samurai
  # Make the samurai user auto-login [*** DO WE REALLY NEED THIS?]
  if [ ! -d "/etc/lightdm/lightdm.conf.d" ]; then
    mkdir /etc/lightdm/lightdm.conf.d
  fi
  echo "[SeatDefaults]" > /etc/lightdm/lightdm.conf.d/50-myconfig.conf
  echo autologin-user=samurai >> /etc/lightdm/lightdm.conf.d/50-myconfig.conf
fi

##################################################################
# TARGETS
##################################################################

echo 'Installing SamuraiWTF targets...'

a2enmod ssl
a2enmod headers
a2dissite 000-default
cp /opt/samurai/install/000-default.conf /etc/apache2/sites-available/
a2ensite 000-default
a2ensite vulnscripts

### TODO: conditionally git clone these
echo 'Installing Samurai Dojo target applications...'
cd /usr/share
git clone https://github.com/SamuraiWTF/Samurai-Dojo.git samurai-dojo
#|cp samurai-dojo/dojo-basic.conf /etc/apache2/sites-available/
#|cp samurai-dojo/dojo-scavenger.conf /etc/apache2/sites-available/
cd /usr/share/samurai-dojo/basic
phpenmod mysqli
php reset-db.php
mysqladmin -u root -psamurai create samurai_dojo_scavenger
mysql -u root -psamurai samurai_dojo_scavenger < /usr/share/samurai-dojo/scavenger/scavenger.sql

a2ensite dojo-basic
a2ensite dojo-scavenger


echo '>>> Installing Mutillidae...'
cd /usr/share
git clone git://git.code.sf.net/p/mutillidae/git mutillidae
# TODO - Fix this cert
cp samurai-dojo/ssl.crt mutillidae/
a2ensite mutillidae


echo '>>> Installing DVWA...'
cd /usr/share
git clone https://github.com/RandomStorm/DVWA.git dvwa
# TODO - Fix this cert
cp samurai-dojo/ssl.crt dvwa/
cd /usr/share/dvwa
sed -i 's/p@ssw0rd/samurai/g' config/config.inc.php
chmod 777 hackable/uploads/
chmod 666 external/phpids/0.6/lib/IDS/tmp/phpids_log.txt
a2ensite dvwa


echo '>>> Installing bWAPP...'
cd /usr/share
git clone git://git.code.sf.net/p/bwapp/code bwapp
cd /usr/share/bwapp/bWAPP
chmod 777 passwords/
chmod 777 images/
chmod 777 documents/
mkdir logs
chmod 777 logs/
sed -i 's/\$db_password = "bug";/\$db_ssword = "samurai";/g' admin/settings.php

# TODO - Initialize DB, etc...
a2ensite bwapp

service apache2 restart

# Make the samurai user auto-login
# TODO: Make this optional since most people really should login :)
if [ ! -d "/etc/lightdm/lightdm.conf.d" ]
then
  mkdir /etc/lightdm/lightdm.conf.d
fi
echo "[SeatDefaults]" > /etc/lightdm/lightdm.conf.d/50-myconfig.conf
echo autologin-user=samurai >> /etc/lightdm/lightdm.conf.d/50-myconfig.conf

# Setup the background
# TODO: This doesn't seem to be working... not sure why
# su - samurai -c 'kwriteconfig --file plasma-appletsrc --group Containments --group 8 --group Wallpaper --group image --key wallpaper /opt/samurai/samurai-background.png'
# su - samurai -c 'gsettings set org.gnome.desktop.background picture-uri file:////opt/samurai/samurai-background.png'
# TODO: Reload plasma to see desktop background.  Maybe not necessary if we just do a reboot?
# pkill plasma
# plasma-desktop &

echo "Additional manual (for now) installation steps:"
echo "- Set the background desktop image to /opt/samurai/samurai-background.png"
echo "- Visit http://bWAPP/install.php and run the install"
echo "- Visit http://mutillidae and reset the database"
echo "- Visit http://dvwa/setup.php and reset the database"


##################################################################
# TOOLS
##################################################################
# echo 'samurai' | sudo -S apt-get install -y python, nikto, w3af-console, w3af, nmap, zenmap, python-pip, apache2, libapache2-mod-php5, mysql-server, libapache2-mod-auth-mysql, php5-mysql, w3af, wireshark, openjdk-7-jre, ruby-full, chromium-browser, firefox, php5-curl, php5-gd
