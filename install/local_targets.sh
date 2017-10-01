#!/bin/bash

echo 'Setting hosts entries for local targets'

echo '127.0.0.1   juice-shop.wtf' | sudo tee -a /etc/hosts
echo '127.0.0.1   dojo-basic.wtf' | sudo tee -a /etc/hosts

sudo mkdir /home/samurai/.scripts
sudo cp /tmp/config/startup_targets.sh /home/samurai/.scripts
sudo chmod -R 755 /home/samurai/.scripts

echo '@reboot root /home/samurai/.scripts/startup_targets.sh &' | sudo tee /etc/cron.d/targets

sudo reboot

#echo '/home/samurai/.scripts/startup_targets.sh' | sudo tee -a /home/samurai/.config/openbox/autostart
#sudo run --rm -p 3000:3000 bkimminich/juice-shop &

#cd /opt/targets/dojo-basic
#sudo docker-compose up &

#sudo service nginx restart;curl http://dojo-basic.wtf/reset-db.php
