# samuraiwtf
Notes: Vagrant plugins used: vagrant-vbguest 

*NOTE: This project should currently be considered experimentation only, as it is not yet ready for release.*
**Want to Contribute? See section at the end of this readme**

The purpose behind this project is to migrate the SamuraiWTF (http://www.samurai-wtf.org), which until now has been maintained as a monolithic virtual machine, to a "packageable" distribution system. The current direction of choice is Vagrant with a VirtualBox provider, which is the effort in this master branch.  Alternative efforts can be found in other branches.

## Vagrant Notes
Vagrant should be used for ongoing development of SamuraiWTF. Development should occur as follows:

## Initial Install
Assuming you have Vagrant installed, just type `vagrant up` from within this folder. Then sit back and wait for it to finish. Immediately after the first time start up it is recommend you do a restart using `vagrant reload`.  Just running the vagrant up will build the primary target, which is a single VM with both the user environment and the targets.  You can run `vagrant up userenv` and vagrant up target to build seperate virtual machines for those purposes.

### Provisioning Scripts
The main Vagrant provisioning script for SamuraiWTF is *install/userenv_bootstrap.sh*.  A standalone targets provisioning script is in *install/target_bootstrap.sh*.  Changes for the system, targets, or tools installation or intialization for SamuraiWTF are all handled within these scripts.

## Production VM Notes:
*TBD*

# Contributors
Contributors are very welcome and the contribution process is standard:

  * fork this project
  * make your contribution
  * submit a pull request
  
Substancial or *Regular* contributors may also be brought in as full team members. This includes those who have made substancial contributions to previous versions of SamuraiWTF with the assumption they will continue to do so.
