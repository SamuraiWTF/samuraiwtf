# samuraiwtf

**Want to Contribute? See section at the end of this readme**

The purpose behind this project is to migrate the SamuraiWTF (http://www.samurai-wtf.org), which until now has been maintained as a monolithic virtual machine, to a "packageable" distribution system. The current direction of choice is Vagrant with a VirtualBox provider, which is the effort in this master branch.  Alternative efforts can be found in other branches.

**To download an OVA to import a full virtual machine, visit https://tiny.si/samurai. 

A [video tutorial](https://www.youtube.com/watch?v=3a3qOFubfGg) is available showing how to install from OVA.

## Prerequisites
- Vagrant - https://www.vagrantup.com/
- Virtualization Software - The base vagrant box used supports virtualbox, vmware, and parallels, but testing at this time has been solely on virtualbox - https://www.virtualbox.org/
- vagrant-vbguest plugin for vagrant (virtualbox only) - this automatically installs guest extensions which provide support for higher display resolutions, as well as other conveniences like clipboard sharing - https://github.com/dotless-de/vagrant-vbguest
- vagrant-reload plugin - this facilitates a necessary reboot during initial provisioning (can be installed with `vagrant plugin install vagrant-reload`).
- Disable Hyper-V (Windows and Virtualbox only) - follow the Resolution instructions provided by Microsoft to disable and enable Hyper-V (requires reboot) - https://support.microsoft.com/en-us/help/3204980/virtualization-applications-do-not-work-together-with-hyper-v-device-g

## Initial Install
1. Make sure you have the prereqs listed above. Webpwnized has made some helpful [YouTube video instructionals](https://www.youtube.com/watch?v=MCqpTpxNSlA&list=PLZOToVAK85Mru8ye3up3VR_jXms56OFE5) for getting Vagrant and VirtualBox  with vbguest plugin installed in case you have not done so before.
2. Clone this repository.
3. From a command-line terminal in the project directory, run the command `vagrant up`. Then sit back and wait for it to finish.

**NOTE: The Guest VM's window will open with the CLI while provisioning is still ongoing. It's best to leave it alone until the `vagrant up` command fully completes.**

### Provisioning Scripts
SamuraiWTF is provisioned through the ansible-local Vagrant provisioner.  Provisioning is organized into the following playbooks, all found in the install folder:

- bootstrap.yml: Prepare the environment to install tools and targets.  A reboot occurs after this playbook runs.
- tools.yml:  Install all tools for the SamuraiWTF environment. Tool installation tasks are found in the install/tools folder.
- targets.yml:  Install all the targets for the SamuraiWTF environment.  Target installation tasks are found in the install/targets folder.
- user.yml:  Finalize any configuration for the samurai user.

## Development
Once you have a running environment, use the ansible playbooks to define any changes or additions to the installation.  To test the change, there is no need to re-run the entire provisioning through Vagrant every time.  Instead, you can just run one of the ansible playbooks from the vagrant folder inside the guest (i.e. first do `vagrant ssh`).  For example, if you are adjusting a tool, you would type:

```
cd /vagrant
ansible-playbook install/tools.yml
```

Note that this is run as the vagrant (non-privileged) user, and does not require sudo.  Ansible will call sudo internally if needed.


## Production VM Notes:
Once you load the VM, the username and password are:

- Username: samurai
- Password: samurai

The menus are available in the top-left corner of the desktop.

Once you log in, there are a couple of things that might need to be adjusted manually.

First, load the Chrome bookmarks by starting *Chrome*.  Then select the *three dots* menu and select *Bookmarks*.
From the sub menu, select *Import bookmarks and settings*.  In the window that opens, select *Bookmarks HTML File*.
A file selector window will open.  Select the *chrome_bookmarks.html* file in the samurai home directory.

## Virtualbox Display
- To automatically adjust the display resolution, do the following:
	- Select Virtualbox Menu -> View
	- Click Auto-Resize Guest Display
	- Resize Virtualbox window and display should change to fit window size.

# License
The scripts and resources belonging to this project itself are licensed under the GNU Public License version 3 (GPL3).
All software loaded into the VM, including the tools, targets, utilities, and operating system itself retain their original license agreements.


# Contributors
Contributors are very welcome and the contribution process is standard:

  * fork this project
  * make your contribution
  * submit a pull request
  
Substantial or *Regular* contributors may also be brought in as full team members. This includes those who have made substantial contributions to previous versions of SamuraiWTF with the assumption they will continue to do so.
