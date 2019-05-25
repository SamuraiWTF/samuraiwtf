<p align="center">
  <img alt="SamuraiWTF Logo" src="https://tiny.si/images/SamuraiWTFLogo.png" height="200"/>
</p>

<p align="center">
  <a href="https://professionallyevil.slack.com/messages/samuraiwtf"> <img alt="Slack" src="https://img.shields.io/badge/chat-ProfessionallyEvil-%238c0000.svg?logo=slack" /></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf/releases"> <img alt="Github" src="https://img.shields.io/github/downloads/SamuraiWTF/samuraiwtf/total.svg?label=Github%20Downloads"/></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf"> <img alt="SourceForge" src="https://img.shields.io/sourceforge/dt/samurai.svg?label=%28Deprecated%29%20%20SourceForge%20Downloads"/></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf/releases"> <img alt="Latest version" src="https://img.shields.io/github/release/SamuraiWTF/samuraiwtf.svg" /></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf/blob/master/LICENSE" > <img alt="License" src="https://img.shields.io/badge/license-GPLv3-blue.svg" /></a>
  <a href="https://twitter.com/intent/tweet?via=secureideas&hashtags=SamuraiWTF%2CProfessionallyEvil&url=https%3A%2F%2Fsamurai.wtf"> <img alt="Twitter Hashtag" src="https://img.shields.io/badge/%23SamuraiWTF-tweet%20about%20us-lightgrey.svg?logo=twitter&style=social" /></a>
  <a href="https://twitter.com/intent/follow?screen_name=secureideas" > <img alt="Twitter handle" src="https://img.shields.io/twitter/follow/secureideas.svg?label=Follow%20%40secureideas%20for%20updates&style=social" /></a>
</p>

----

**Want to chat with us? Come message us in the [Professionally Evil slack][samurai-slack-url].**

**Want to Contribute? See [here](#Contributors)**

The purpose behind this project is to migrate the SamuraiWTF (http://www.samurai-wtf.org), which until now has been maintained as a monolithic virtual machine, to a "packageable" distribution system. The current direction of choice is Vagrant with a VirtualBox provider, which is the effort in this master branch.  Alternative efforts can be found in other branches.

**NOTE:** for getting started quickly you can follow the ova installation [here](#OVA)

## Prerequisites
- Vagrant - https://www.vagrantup.com/
- Virtualization Software - The base vagrant box used supports virtualbox, vmware, and parallels, but testing at this time has been solely on virtualbox - https://www.virtualbox.org/
- vagrant-vbguest plugin for vagrant (virtualbox only) - this automatically installs guest extensions which provide support for higher display resolutions, as well as other conveniences like clipboard sharing - https://github.com/dotless-de/vagrant-vbguest
- vagrant-reload plugin - this facilitates a necessary reboot during initial provisioning (can be installed with `vagrant plugin install vagrant-reload`).
- Disable Hyper-V (Windows and Virtualbox only) - follow the Resolution instructions provided by Microsoft to disable and enable Hyper-V (requires reboot) - https://support.microsoft.com/en-us/help/3204980/virtualization-applications-do-not-work-together-with-hyper-v-device-g

## Initial Install
### OVA
1. Make sure you have the Virtualization Software and Disabled Hyper-V from the prereqs [above](#Prerequisites)
2. Download the OVA to import a full virtual machine, here: https://tiny.si/samurai.
3. Watch this [video tutorial](https://www.youtube.com/watch?v=3a3qOFubfGg), made by [webpwnized](https://twitter.com/webpwnized), which shows you how to install SamuraiWTF using the OVA.

### Vagrant
1. Make sure you have the prereqs listed [above](#Prerequisites). Webpwnized has made some helpful [YouTube video instructionals](https://www.youtube.com/watch?v=MCqpTpxNSlA&list=PLZOToVAK85Mru8ye3up3VR_jXms56OFE5) for getting Vagrant and VirtualBox with vbguest plugin installed in case you have not done so before.
2. Clone this repository.
3. From a command-line terminal in the project directory, run the command `vagrant up`. Then sit back and wait for it to finish.
4. (Optional) If you want to understand this process a little more, we have a video that discusses what is happening with more detail. It is listed as a free course on our training site: https://training.secureideas.com/course/foldingsteel/

**NOTE: The Guest VM's window will open with the CLI while provisioning is still ongoing. It's best to leave it alone until the `vagrant up` command fully completes.**

#### Provisioning Scripts
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

_Note that this is run as the vagrant (non-privileged) user, and does not require sudo.  Ansible will call sudo internally if needed._

### Development Guidelines

- Our integration branch is the one called `next`. That's where all new features and bug fixes go for testing before a release.  The `master` branch should be kept stable at all times.
- Larger changes should be done in separate feature branches.  Make sure to merge `next` into your feature branch, then PR the feature branch to merge into `next`.
- If you break `next` or `master`, fix it (with help if necessary). It's best to run a full test build (i.e. `vagrant destroy`, `vagrant up`) and make sure tools ard targets are working before pushing changes.

### Expected Errors
Sometimes there are some expected errors during the build process.  

- There is one scary error in the _Install Docker_ task for VirtualBox provisioning that looks like it fails miserably.  At the bottom of that error output you will see the message `...ignoring` .  This is because our ansible playbook is expecting the error and moves on to the next task. Docker should still have installed but it had trouble getting to the right version of certain a kernel library due to an upgrade of guest additions. This should resolve itself once the system reboots (which should happen automatically).

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

[samurai-slack-url]: https://professionallyevil.slack.com/messages/samuraiwtf
