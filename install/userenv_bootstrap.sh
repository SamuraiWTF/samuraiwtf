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

#switch to the samurai user for permissions
sudo su - samurai

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

echo '...installing from debian repos...'
sudo apt-get install -y firefox-esr leafpad

###Nikto missing, along with SQL map, word lists, firefox plugins
sudo apt-get install -y w3af w3af-console nmap zenmap unzip build-essentials #wireshark

#Wireshark requires an input atm, probably need to deb-conf it
#w3af_console tried to run /usr/bin/python2.5 (quick and dirty fix might be to create a symlink)
#some zenmap features require sudo - need to add it to the ob menu a "gksudo zenmap"

###JRE
sudo apt-get install -y  default-jre

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
sudo curl -s -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
echo '...Docker Compose installed.'

echo 'Setting up wpscan'
sudo docker pull wpscanteam/wpscan


echo '...fetching installers...'
sudo mkdir /tmp/installers
sudo mkdir /opt/samurai
sudo chown samurai:samurai /opt/samurai
sudo chmod 777 /tmp/installers

cd /opt/samurai

mkdir /opt/samurai/burpsuite
wget -q -O /opt/samurai/burpsuite/burp.jar https://portswigger.net/burp/releases/download?productid=100&type=jar

# install Nikto from Git at https://github.com/sullo/nikto.git
git clone https://github.com/sullo/nikto.git

# install sqlmap from Git at https://github.com/sqlmapproject/sqlmap.git
git clone https://github.com/sqlmapproject/sqlmap.git

# install fuzzdb from Git at https://github.com/fuzzdb-project/fuzzdb.git
git clone https://github.com/fuzzdb-project/fuzzdb.git

# installing ZAP from the OWASP download site on Git
wget -q -O https://github.com/zaproxy/zaproxy/releases/download/2.6.0/ZAP_2.6.0_Crossplatform.zip /tmp/installers/
unzip /tmp/installers/ZAP_2.6.0_Crossplatform.zip 

#Hack to fix w3af_console
sudo ln -s /usr/bin/python /usr/bin/python2.5

echo 'copying launch scripts to /usr/bin'
sudo cp /tmp/config/launcher/* /usr/bin/

###############################################
# FIREFOX CONFIG 
###############################################

echo 'installing and configuring plugins for Firefox'

#install node.js because Mozilla hates people
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs






mkdir /tmp/extensions
#sudo mkdir /usr/share/mozilla/extensions
#wget -q -O foxyproxy.xpi https://addons.mozilla.org/firefox/downloads/latest/foxyproxy-standard/addon-2464-latest.xpi
#unzip foxyproxy.xpi
#rm foxyproxy.xpi
#mkdir /usr/share/mozilla/extensions/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}

###############################################
# USER CONFIG (Should be changed to samurai)
###############################################

echo 'Setting up user config...'

sudo touch /var/log/vagrantup.log
sudo chown vagrant /var/log/vagrantup.log

sudo cp -v /tmp/config/xinitrc /home/samurai/.xinitrc
sudo cp -v /tmp/config/bashprofile /home/samurai/.bash_profile

sudo mkdir -v /home/samurai/.config >> /var/log/vagrantup.log
sudo cp -v /tmp/config/tint2.conf /home/samurai/.config/

sudo mkdir -v /home/samurai/.config/openbox >> /var/log/vagrantup.log
sudo cp -v /tmp/config/openbox.autostart /home/samurai/.config/openbox/autostart

sudo mkdir -v /home/samurai/.config/wallpaper >> /var/log/vagrantup.log
sudo cp -v /tmp/config/samurai-background.png /home/samurai/.config/wallpaper

echo "feh --bg-fill '/home/samurai/.config/wallpaper/samurai-background.png'" >> /home/samurai/.fehbg

sudo cp /tmp/config/menu.xml /home/samurai/.config/openbox/
sudo cp /tmp/config/openbox_rc.xml /home/samurai/.config/openbox/rc.xml

sudo mkdir /home/samurai/.config/tilda
sudo cp /tmp/config/tilda_config_0 /home/samurai/.config/tilda/config_0

sudo chown -R samurai /home/samurai

#echo "xcompmgr -c &" >> /home/samurai/.config/openbox/autostart
#echo "tint2 &" >> /home/samurai/.config/openbox/autostart

echo 'All finished!'
