#!/bin/bash

sudo amazon-linux-extras install ansible2

pushd ~ || exit

git clone --depth=1 --single-branch --branch --branch "5.0-dev" https://github.com/SamuraiWTF/samuraiwtf.git

cd samuraiwtf || exit

sudo ansible-playbook -K base/amazon-linux/local_playbook.yml

sudo mkdir -p /opt/katana
sudo cp -R katana/* /opt/katana/

popd