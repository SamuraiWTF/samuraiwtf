# Packer build for samuraiwtf

*NOTE: This project should currently be considered experimentation only, as it is not yet ready for release.*

*NOTE: At present there are issues with Packer that are preventing a build from completing.*

## Pre-requisites
We have elected to use the vm image builders instead of the iso builders due to complications with building desktop images from ISOs in packer.io (yes, it is possible - just too cludgy to be bothered with).  Therefore, you will need to begin by creating a base Ubuntu desktop virtual machine. This starter image should be set up as follows:

* The VM should have at least 2GB RAM
* The user should be "samurai" with the password "samurai". (This is just for installation and may be changed later.)
* ssh must be installed so that the packer.io template can connect to it.  To do this, simply run from the command line: ```sudo apt-get update; sudo apt-get install -y openssh-server```

If you don't want to modify all the packer scripts, you must set the path of the starter vms as follows:

* **VMWare:** *packer-templates/base-vm/vmware/ubuntu-16.04.2-desktop.vmx*

These paths can be found in the appropriate section of any *packer-templates/template.json* file.

## Building
Assuming you have installed packer (see https://www.packer.io/ if you haven't)...

Just cd to *packer-templates/* and run packer, e.g.: ```packer build ubuntu_16_04.json```

## Known Issues
* Packer, for reasons unknown, fails to locate the Output VM when it tries to post-process it. This results in an error state, which causes packer to delete the resulting output VM.