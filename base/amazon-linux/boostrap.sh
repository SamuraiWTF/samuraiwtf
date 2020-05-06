#!/bin/bash

sudo amazon-linux-extras install ansible2

cd samuraiwtf || exit

sudo ansible-playbook -K base/amazon-linux/local_playbook.yml

if [[ "$1" == "--develop" ]]; then
  sudo ln -s "$(pwd)/katana/" /opt/katana
else
  sudo mkdir -p /opt/katana
  sudo cp -R katana/* /opt/katana/
fi