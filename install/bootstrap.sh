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
################################################

sudo apt-get install -y vim

################################################
# TARGETS
################################################

# Placeholder for targets

####### NOTHING FOR THE TARGET SERVER SHOULD BE BELOW THIS POINT ######

################################################
# TRAINING USER CREATE
################################################
# quietly add a user without password
sudo adduser --quiet --disabled-password --ingroup sudo --shell /bin/bash --home /home/samurai --gecos "Samurai" samurai

# set password
echo "samurai:samurai" | sudo chpasswd

################################################
# GUI
################################################

sudo apt-get install -y xauth
sudo apt-get install -y xorg
sudo apt-get install -y openbox

sudo apt-get install -y tint2 xcompmgr feh

################################################
# TOOLS
################################################

# Placeholder for tools

###############################################
# USER CONFIG (Should be changed to samurai)
###############################################

sudo cp /tmp/config/xinitrc /home/samurai/.xinitrc
sudo cp /tmp/config/bashprofile /home/samurai/.bash_profile

sudo mkdir /home/samurai/.config
sudo cp /tmp/config/tint2.conf /home/samurai/.config/

sudo mkdir /home/samurai/.config/openbox
sudo cp /tmp/config/openbox.autostart /home/samurai/.config/openbox/autostart

sudo mkdir /home/samurai/.config/wallpaper
sudo cp /tmp/config/samurai-background.png /home/samurai/.config/wallpaper

echo "feh --bg-scale '/home/samurai/.config/wallpaper/samurai-background.png'" >> /home/samurai/.fehbg

sudo chown -R samurai /home/samurai

#echo "xcompmgr -c &" >> /home/samurai/.config/openbox/autostart
#echo "tint2 &" >> /home/samurai/.config/openbox/autostart
