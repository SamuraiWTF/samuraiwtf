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

add-apt-repository -y ppa:kubuntu-ppa/backports
apt-get install -y kubuntu-desktop

if [ ! -d /opt/samurai ]; then
	echo 'Removing unecessary default packages...'
	apt-get remove -y --purge libreoffice*
	apt-get remove -y --purge thunderbird
	apt-get -y clean
	apt-get -y autoremove
else
	echo 'Skipping removal of default packages'
fi
echo 'Running updates...'
apt-get update
apt-get -y upgrade

# Set locale (Fixes broken terminal)
locale-gen "en_US.UTF-8"
localectl set-locale LANG="en_US.UTF-8"

echo 'Installing AMP stack...'
if [ ! -d /opt/samurai ]; then
	apt-get install -y mysql-server
	mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'samurai';"	
else
	apt-get install -y mysql-server
fi

# Dependencies...
apt-get install -y git apache2 php php-mysql libapache2-mod-php php-gd php-curl

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

# TODO: Reload the menu (not sure why this isn't happening on restart like it did in Ubuntu 14.04)
#       may need to move apps to ~/.local/share/applications or /usr/share/applications
# TODO: Turn off lock screen

# Some cosmetics... these don't seem to be taking?
# gsettings set com.canonical.Unity.Launcher favorites "['application://ubiquity.desktop', 'application://org.gnome.Nautilus.desktop', 'application://firefox.desktop','application://chromium-browser.desktop','application://unity-control-center.desktop', 'application://gnome-terminal.desktop', 'unity://running-apps', 'unity://expo-icon', 'application://samurai.desktop']"
# gsettings set org.gnome.desktop.background picture-uri 'file:///opt/samurai/samurai-background.png'
# gsettings set com.canonical.Unity.Launcher launcher-position 'Bottom'
# gsettings set org.gnome.desktop.screensaver lock-enabled false

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

# Samurai Dojo
if [ ! -d /usr/share/samurai-dojo ]; then
	echo 'Installing Samurai Dojo...'
	cd /usr/share
	git clone https://github.com/SamuraiWTF/Samurai-Dojo.git samurai-dojo
	cd /usr/share/samurai-dojo/basic
	phpenmod mysqli
	php reset-db.php
	mysqladmin -u root -psamurai create samurai_dojo_scavenger
	mysql -u root -psamurai samurai_dojo_scavenger < /usr/share/samurai-dojo/scavenger/scavenger.sql
	a2ensite dojo-basic
	a2ensite dojo-scavenger
else
	echo 'Updating Samurai Dojo...'
	cd /usr/share/samurai-dojo
	git pull
fi

# Mutillidae
if [ ! -d /usr/share/mutillidae ]; then
	echo 'Installing Mutillidae...'
	cd /usr/share
	git clone git://git.code.sf.net/p/mutillidae/git mutillidae
	# TODO - Fix this cert
	cp samurai-dojo/ssl.crt mutillidae/
	a2ensite mutillidae
	# TODO: Automate this
	echo "- Visit http://mutillidae and reset the database"
else
	echo 'Updating Mutillidae...'
	cd /usr/share/mutillidae
	git pull
fi

# DVWA
if [ ! -d /usr/share/dvwa ]; then
	echo 'Installing DVWA...'
	cd /usr/share
	git clone https://github.com/RandomStorm/DVWA.git dvwa
	# TODO - Fix this cert
	cp samurai-dojo/ssl.crt dvwa/
	cd /usr/share/dvwa
	sed -i 's/p@ssw0rd/samurai/g' config/config.inc.php
	chmod 777 hackable/uploads/
	chmod 666 external/phpids/0.6/lib/IDS/tmp/phpids_log.txt
	a2ensite dvwa
	## TODO: automate this:
	echo "- Visit http://dvwa/setup.php and reset the database"
else
	echo 'Updating DVWA...'
	cd /usr/share/dvwa
	git pull
fi

# bWAPP
if [ ! -d /usr/share/bwapp ]; then
	echo 'Installing bWAPP...'
	cd /usr/share
	git clone git://git.code.sf.net/p/bwapp/code bwapp
	cd /usr/share/bwapp/bWAPP
	chmod 777 passwords/
	chmod 777 images/
	chmod 777 documents/
	mkdir logs
	chmod 777 logs/
	sed -i 's/\$db_password = "bug";/\$db_password = "samurai";/g' admin/settings.php
	a2ensite bwapp
	curl -s http://bwapp/install.php?install=yes > /dev/null
else
	echo 'Updating bWAPP...'
	cd /usr/share/bwapp
	git pull
fi

service apache2 restart

# Setup the background
# TODO: This doesn't seem to be working... not sure why
# su - samurai -c 'kwriteconfig --file plasma-appletsrc --group Containments --group 8 --group Wallpaper --group image --key wallpaper /opt/samurai/samurai-background.png'
# su - samurai -c 'gsettings set org.gnome.desktop.background picture-uri file:////opt/samurai/samurai-background.png'
# TODO: Reload plasma to see desktop background.  Maybe not necessary if we just do a reboot?
# pkill plasma
# plasma-desktop &
echo "Additional manual (for now) installation steps:"
echo "- Set the background desktop image to /opt/samurai/samurai-background.png"



##################################################################
# TOOLS
##################################################################
# echo 'samurai' | sudo -S apt-get install -y python, nikto, w3af-console, w3af, nmap, zenmap, python-pip, apache2, libapache2-mod-php5, mysql-server, libapache2-mod-auth-mysql, php5-mysql, w3af, wireshark, openjdk-7-jre, ruby-full, chromium-browser, firefox, php5-curl, php5-gd

apt-get install -y nikto w3af-console w3af nmap zenmap python-pip w3af wireshark openjdk-9-jre ruby-full chromium-browser

