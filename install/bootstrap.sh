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

#Re-enable (disabled for dev to cut rebuild time)
#sudo apt-get upgrade

echo "deb http://ftp.debian.org/debian jessie-backports main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update

################################################
# BASIC UTILS (Required for either target server or full environment)
###############################################


echo 'Installing basic system utils...'

sudo apt-get install -y vim python-pip

###Ruby/RVM

###Python/Pip?

################################################
# TARGETS
################################################

###DOCKER?

echo 'Installing training targets...'

# Placeholder for targets

###Possibly Nginx (reverse proxy)

####### NOTHING FOR THE TARGET SERVER SHOULD BE BELOW THIS POINT ######

################################################
# TRAINING USER CREATE
################################################
# quietly add a user without password
echo 'Checking for Samurai user...'
USERCOUNT=`cat /etc/passwd |grep "samurai:" | wc -l`
if [ $USERCOUNT -eq 0 ]; then
  echo "It looks like the samurai user does not exist.  Creating..."
  useradd -d /home/samurai -U -m -s /bin/bash -G sudo -p b.jPTlW8tPfR6 samurai
else
	echo "Samurai user appears to already exist"
fi

################################################
# GUI
################################################

echo 'Installing GUI packages...'

sudo apt-get install -y xauth
sudo apt-get install -y xorg
sudo apt-get install -y openbox

sudo apt-get install -y tint2 xcompmgr feh tilda

################################################
# TOOLS
################################################

echo 'Installing tools...'

sudo apt-get install -y firefox-esr leafpad

###Nikto missing, along with SQL map, word lists, firefox plugins
sudo apt-get install -y w3af w3af-console nmap zenmap #wireshark

#Wireshark requires an input atm, probably need to deb-conf it
#w3af_console tried to run /usr/bin/python2.5 (quick and dirty fix might be to create a symlink)
#some zenmap features require sudo - need to add it to the ob menu a "gksudo zenmap"

###JRE

###Need to work out burp

#wget -O burp.jar https://portswigger.net/burp/releases/download?productid=100&type=jar
#mkdir /usr/share/burp
#mv burp.jar /usr/share/burpsuite_free/burp.jar

#sudo apt-get install -y mozilla-firefox chromium-browser

###############################################
# USER CONFIG (Should be changed to samurai)
###############################################

echo 'Setting up user config...'

sudo touch /var/log/vagrantup.log
sudo chown vagrant /var/log/vagrantup.log

sudo cp -v /tmp/config/xinitrc /home/samurai/.xinitrc >> /var/log/vagrantup.log
sudo cp -v /tmp/config/bashprofile /home/samurai/.bash_profile >> /var/log/vagrantup.log

sudo mkdir -v /home/samurai/.config >> /var/log/vagrantup.log
sudo cp -v /tmp/config/tint2.conf /home/samurai/.config/ >> /var/log/vagrantup.log

sudo mkdir -v /home/samurai/.config/openbox >> /var/log/vagrantup.log
sudo cp -v /tmp/config/openbox.autostart /home/samurai/.config/openbox/autostart >> /var/log/vagrantup.log

sudo mkdir -v /home/samurai/.config/wallpaper >> /var/log/vagrantup.log
sudo cp -v /tmp/config/samurai-background.png /home/samurai/.config/wallpaper >> /var/log/vagrantup.log

echo "feh --bg-fill '/home/samurai/.config/wallpaper/samurai-background.png'" >> /home/samurai/.fehbg

sudo cp /tmp/config/menu.xml /home/samurai/.config/openbox/

sudo mkdir /home/samurai/.config/tilda
sudo cp /tmp/config/tilda_config_0 /home/samurai/.config/tilda/config_0

sudo chown -R samurai /home/samurai

#echo "xcompmgr -c &" >> /home/samurai/.config/openbox/autostart
#echo "tint2 &" >> /home/samurai/.config/openbox/autostart

echo 'All finished!'
