#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo amazon-linux-extras install ansible2

pushd "$DIR"/../.. || exit

sudo ansible-playbook -K base/amazon-linux/local_playbook.yml

sudo openssl genrsa -out /etc/samurai.d/certs/rootCAKey.pem 2048
sudo openssl req -x509 -sha256 -new -nodes -key /etc/samurai.d/certs/rootCAKey.pem -days 365 -out /etc/samurai.d/certs/rootCACert.pem -subj "/C=US/ST=Hacking/L=Springfield/O=SamuraiWTF/CN=samuraiwtf"
sudo cp /etc/samurai.d/certs/rootCACert.pem /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
sudo openssl req -new -newkey rsa:4096 -nodes -keyout /etc/samurai.d/certs/katana.test.key -out /etc/samurai.d/certs/katana.test.csr -subj "/C=US/ST=Hacking/L=Springfield/O=SamuraiWTF/CN=katana.test"


katana --update updates/2022-02-rollup

katana install katana

popd

sudo systemctl enable samurai-katana

sudo systemctl enable docker
