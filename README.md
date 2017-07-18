# samuraiwtf
Notes: Vagrant plugins used: vagrant-vbguest vagrant-hostsupdater

*NOTE: This is an experimental fork of the already experimental build. It's **not ready** for general consumption.*

**Everything below this line is from the original readme**

*NOTE: This project should currently be considered experimentation only, as it is not yet ready for release.*

The purpose behind this project is to migrate the SamuraiWTF (http://www.samurai-wtf.org), which until now has been maintained as a monolithic virtual machine, to a "packageable" distribution system. At present there are three solutions in this project in varying states of useability:

1. Under *samuraiwtf-deb/* there is a Debian package installation, which should be considered the legacy solution but is still being referenced.
2. Under *packer-templates/* there are packer.io templates for building the SamuraiWTF Virtual Machine from scratch (almost).
3. Under *install/* there are build scripts that are designed to work with both the Vagrantfile in this folder as well as be imported into a vanilla install of Ubuntu desktop (16.04 Xenial). This last method is currently the recommended approach to installing.


## Vagrant Notes
Vagrant should be used for ongoing development of SamuraiWTF. Development should occur as follows:

## Initial Install
Assuming you have Vagrant installed, just type `vagrant up` from within this folder. Then sit back and wait for it to finish. Immediately after the first time start up it is recommend you do a restart using `vagrant reload`.

### Files
The following folders under *samuraiwtf-deb/* are shared under the guest folder */tmp/samuraiwtf/* :

* /usr
* /etc
* /opt
* /var

All the files in these folder get copied into their respective locations during Vagrant provisioning.  When making changes to files for the SamuraiWTF environment, the recommended approach is to make changes in these shared versions of the files (either in /tmp/samuraiwtf/ or in the respective host folder) and then run `vagrant provision` to deploy them.

### Provisioning Script
The main Vagrant provisioning script is *install/bootstrap.sh*.  Changes for the system, targets, or tools installation or intialization for SamuraiWTF are all handled within this script.

## Production VM Notes:
*TBD*

## TODO
### Vagrant Config
- [ ] Combine Targets and base system
