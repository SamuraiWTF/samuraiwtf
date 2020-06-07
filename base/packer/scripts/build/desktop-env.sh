#!/usr/bin/env bash

set -exu
export DEBIAN_FRONTEND='noninteractive'

apt-get update

apt-get -y install aufs-tools cgroupfs-mount mate-desktop-environment
# removing because it gets installed by mate-desktop-environment
apt-get -y purge gdm3
# installing seperatly because of weird conflict with gdm3
apt-get -y install lightdm

reboot
