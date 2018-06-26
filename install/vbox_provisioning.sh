#! /bin/bash

###########################################
## REINSTALL GUEST ADDITIONS
###########################################

export VBOX_LATEST=$(curl http://download.virtualbox.org/virtualbox/LATEST-STABLE.TXT)
export VBOX_LINK=http://download.virtualbox.org/virtualbox/$VBOX_LATEST/VBoxGuestAdditions_$VBOX_LATEST.iso
curl $VBOX_LINK > /tmp/VBoxGuestAdditions.iso
mkdir /media/iso
mount -o loop /tmp/VBoxGuestAdditions.iso /media/iso
sh /media/iso/VBoxLinuxAdditions.run
umount /media/iso