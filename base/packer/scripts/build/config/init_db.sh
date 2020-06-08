#!/bin/bash
id=$(sudo docker ps -aqf "name=scavengerdb")
sudo docker cp ./scavenger.sql $id:/
sudo docker exec $id /bin/sh -c 'mysql -u root -psamurai samurai_dojo_scavenger </scavenger.sql'

