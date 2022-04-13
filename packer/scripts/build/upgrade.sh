#!/bin/sh -eux

export DEBIAN_FRONTEND='noninteractive'

apt-get update && \
    apt-get -y upgrade -o Dpkg::Options::='--force-confold' && \
    apt-get -y dist-upgrade -o Dpkg::Options::='--force-confold' && \
    apt-get -y autoremove
