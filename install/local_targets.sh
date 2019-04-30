#!/bin/bash

echo 'Setting hosts entries for local targets'

echo '# 127.0.0.0/24 are training targets' | sudo tee -a /etc/hosts
echo '127.0.0.1   dojo-basic.wtf' | sudo tee -a /etc/hosts
echo '127.0.0.2   dvwa.wtf' | sudo tee -a /etc/hosts
echo '127.0.0.3   mutillidae.wtf' | sudo tee -a /etc/hosts
echo '127.0.0.4   api.cors.dem' | sudo tee -a /etc/hosts

echo '# 127.0.10.0/24 are training client systems' | sudo tee -a /etc/hosts
echo '127.0.10.1   professionallyevil.wtf' | sudo tee -a /etc/hosts
echo '127.0.10.2   amoksecurity.wtf' | sudo tee -a /etc/hosts
echo '127.0.10.3   client.cors.dem' | sudo tee -a /etc/hosts

echo '# 127.0.42.0/24 are the CtF targets' | sudo tee -a /etc/hosts
echo '127.0.42.42   juice-shop.wtf' | sudo tee -a /etc/hosts
echo '127.0.42.41   dojo-scavenger.wtf' | sudo tee -a /etc/hosts

sudo mkdir /home/samurai/.scripts
sudo tr '\r\n' '\n' < /tmp/config/startup_targets.sh > /home/samurai/.scripts/startup_targets.sh
sudo chmod -R 755 /home/samurai/.scripts

echo '@reboot root /home/samurai/.scripts/startup_targets.sh &' | sudo tee /etc/cron.d/targets

# sudo reboot

#echo '/home/samurai/.scripts/startup_targets.sh' | sudo tee -a /home/samurai/.config/openbox/autostart
#sudo run --rm -p 3000:3000 bkimminich/juice-shop &

#cd /opt/targets/dojo-basic
#sudo docker-compose up &

#sudo service nginx restart;curl http://dojo-basic.wtf/reset-db.php
