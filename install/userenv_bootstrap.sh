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

################################################
# BASIC UTILS (Required for either target server or full environment)
###############################################

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
  sudo -u samurai mkdir /home/samurai/Downloads
else
	echo "Samurai user appears to already exist"
fi


################################################
# GUI
################################################

echo 'Installing GUI packages...'

apt-get install -y xauth
apt-get install -y xorg
apt-get install -y openbox

# This is a deprecated package in ubuntu so might cause problems in future releases.
apt-get install -y gksu

#sudo apt-get install -y tint2 xcompmgr feh tilda xfe network-manager network-manager-gnome arandr
apt-get install -y tint2 xcompmgr feh tilda xfe arandr

################################################
# TOOLS
################################################

echo 'Installing tools...'

echo '...installing from debian repos...'
apt-get install -y sakura firefox-esr leafpad

###Nikto missing, along with SQL map, word lists, firefox plugins
apt-get install -y nmap zenmap unzip build-essential python-pip

#w3af w3af-console - need to be fetched from git repo https://github.com/andresriancho/w3af.git



#Wireshark requires an input atm, probably need to deb-conf it
#w3af_console tried to run /usr/bin/python2.5 (quick and dirty fix might be to create a symlink)
#some zenmap features require sudo - need to add it to the ob menu a "gksudo zenmap"

echo '...installing Google Chrome browser...'
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install -y google-chrome-stable

echo '...installing Google Chrome extensions...'
mkdir /opt/google/chrome/extensions
cp /tmp/config/crx/*.json /opt/google/chrome/extensions/

###JRE
echo '...installing Java Runtime Environment...'
apt-get install -y  default-jre

echo 'Setting up wpscan'
docker pull wpscanteam/wpscan


echo '...fetching installers...'
mkdir /tmp/installers
mkdir /opt/samurai
chown samurai:samurai /opt/samurai
chmod 777 /tmp/installers

cd /opt/samurai

sudo -u samurai mkdir /opt/samurai/burpsuite
sudo -u samurai wget -q -O /opt/samurai/burpsuite/burp.jar https://portswigger.net/burp/releases/download?product=community&type=jar

# install Nikto from Git at https://github.com/sullo/nikto.git
echo '...fetching nikto from github...'
sudo -u samurai git clone --depth=1 https://github.com/sullo/nikto.git

# install sqlmap from Git at https://github.com/sqlmapproject/sqlmap.git
echo '...fetching sqlmap from github...'
sudo -u samurai git clone --depth=1 https://github.com/sqlmapproject/sqlmap.git

# install fuzzdb from Git at https://github.com/fuzzdb-project/fuzzdb.git
echo '...fetching fuzzdb from github...'
sudo -u samurai git clone --depth=1 https://github.com/fuzzdb-project/fuzzdb.git

echo '...fetching seclists from github...'
sudo -u samurai git clone --depth=1 https://github.com/danielmiessler/SecLists.git

# installing ZAP from the OWASP download site on Git
echo '...fetching and unzipping ZAP from github...'
sudo -u samurai wget -q -O /tmp/installers/ZAP_2.6.0_Crossplatform.zip https://github.com/zaproxy/zaproxy/releases/download/2.6.0/ZAP_2.6.0_Crossplatform.zip
sudo -u samurai unzip /tmp/installers/ZAP_2.6.0_Crossplatform.zip

#Hack to fix w3af_console
ln -s /usr/bin/python /usr/bin/python2.5

echo 'copying launch scripts to /usr/bin'

pushd /tmp/config/launcher
for f in ./*
do
	sudo tr '\r\n' '\n' < "$f" > "/usr/bin/$f";
    echo "Adding Execute to $f";
    sudo chmod 755 "/usr/bin/$f";
done
popd

# Download burp plugins for offline installation
echo '...downloading burp plugins to /home/samurai/Downloads folder...'
sudo -u samurai curl https://portswigger.net/bappstore/bapps/download/c5071c7a7e004f72ae485e8a72911afc > /home/samurai/Downloads/co2.bapp
sudo -u samurai curl https://portswigger.net/bappstore/bapps/download/0ac13c45adff4e31a3ca8dc76dd6286c > /home/samurai/Downloads/paramalyzer.bapp
sudo -u samurai curl https://portswigger.net/bappstore/bapps/download/594a49bb233748f2bc80a9eb18a2e08f > /home/samurai/Downloads/wsdler.bapp

# Add Postman
echo '...downloading and unzipping latest postman tar...'
curl https://dl.pstmn.io/download/latest/linux64 > /tmp/postman.tgz
tar -zxvf /tmp/postman.tgz --directory=/opt/samurai/
rm /tmp/postman.tgz

###############################################
# FIREFOX CONFIG
###############################################

echo 'installing and configuring plugins for Firefox'

#install node.js because Mozilla hates people
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
apt-get install -y nodejs

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

touch /var/log/vagrantup.log
chown vagrant /var/log/vagrantup.log

cp -v /tmp/config/xinitrc /home/samurai/.xinitrc
cp -v /tmp/config/bashprofile /home/samurai/.bash_profile

mkdir -v /home/samurai/.config >> /var/log/vagrantup.log
cp -v /tmp/config/tint2.conf /home/samurai/.config/

mkdir -v /home/samurai/.config/openbox >> /var/log/vagrantup.log
cp -v /tmp/config/openbox.autostart /home/samurai/.config/openbox/autostart

mkdir -v /home/samurai/.config/wallpaper >> /var/log/vagrantup.log
cp -v /tmp/config/samurai-background.png /home/samurai/.config/wallpaper

echo "feh --bg-fill '/home/samurai/.config/wallpaper/samurai-background.png'" >> /home/samurai/.fehbg

cp /tmp/config/menu.xml /home/samurai/.config/openbox/
cp /tmp/config/openbox_rc.xml /home/samurai/.config/openbox/rc.xml

mkdir /home/samurai/.config/tilda
cp /tmp/config/tilda_config_0 /home/samurai/.config/tilda/config_0

cp -r /tmp/config/home/* /home/samurai/

chown -R samurai /home/samurai

#echo "xcompmgr -c &" >> /home/samurai/.config/openbox/autostart
#echo "tint2 &" >> /home/samurai/.config/openbox/autostart

echo 'samurai user environment all finished!'
