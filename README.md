<p align="center">
  <img alt="SamuraiWTF Logo" src="http://tiny.si/images/owasp_samurai_v3.png"  height="400"/>
</p>

## Samurai Web Training Framework 5.0

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

This project is not a vulnerable application. It is a framework designed for quickly configuring training virtual machines with tools and vulnerable application targets. This of this as a base box with a specialized package manager.
For example, an instructor could use SamuraiWTF to easily set up a classroom virtual machine image containing OWASP ZAP and OWASP Juice Shop, and then distribute it to each student.

This project includes and uses the [Samurai Katana][samurai-katana-url] project to manage installation and running of tools and targets in the virtual environment. 

**Want to chat with us? Join us in either the OWASP Slack #project-samuraiwtf channel or visit us in [Professionally Evil slack][samurai-slack-url].**

**Want to Contribute? See [here](#Contributors)**

**NOTE:** for getting started quickly you can follow the ova installation [here](#OVA)

**Art Credit:** the above Samurai figure is the original work of Ben Faircloth, who has granted the OWASP SamuraiWTF project permission to use in the product and websites. 

## Initial Install
There are several options for the initial install, as follows:

### Vagrant (Preferred)
Starting with version 5.0 of SamuraiWTF we now use an Ubuntu-based basebox that has most of the prerequisites pre-installed so you can get up and running quickly.

1. Make sure you have Oracle VirtualBox installed (see above [OVA section](#OVA))
2. Clone this repository.
3. From a command-line terminal in the root project folder, run the command `vagrant up`. Then sit back and wait for it to finish.

**note**: The login is samurai/samurai

### OVA on Oracle VirtualBox
1. Make sure you have the Oracle VirtualBox installed, and if you are in Windows you should disable Hyper-V [(Instructions from Microsoft)](https://support.microsoft.com/en-us/help/3204980/virtualization-applications-do-not-work-together-with-hyper-v-device-g).
2. Download the OVA to import a full virtual machine, here: https://tiny.si/samurai-5.0

**note**: The login is samurai/samurai

### AWS Workspace
We have a method of bootstrapping SamuraiWTF into an AWS Workspace (running AWS Linux). This can be useful in situations an instructor wants to set up a remotely accessible SamuraiWTF environment.

1. Make sure you have an AWS account plus the AWS Workspaces client.
2. Create a Workspace with Amazon Linux and 4GB of RAM
3. Log in to the workspace and clone this GitHub repository.
4. Navigate into `samuraiwtf/base/amazon-linux` and run the `bootstrap.sh` shell script. This should set up the rest of what you need.

**note**: The login is your AWS Workspace username and password.

## Lab Quick Setup
Once you log in to the environment, you can install tools and targets using katana either from the command line, or from a browser.

### Command Line
Simply use the command `katana list` to see which packages are available, then install any package with `katana install <package>`. For example, to install ZAP and JuiceShop:

```shell script
katana install zap
katana install juice-shop
katana start juice-shop
```

## Web UI
The web UI can be seen in a browser by visiting `http://katana.wtf`.

If it is not running, you may first need to use the command line to install and start katana. This is done with the commands:
```shell script
katana install katana
katana start katana
```

More detailed instructions on using Katana are available in the readme of the [Samurai Katana][samurai-katana-url] GitHub project.

**IMPORTANT**: Be aware that Katana runs with root privileges and is not intended to be run in a secure or production environment.

## Development
Most of the development in this repo is related to updating basebox provisioning scripts and supporting additional platforms.


- Our integration branch is the one called `next`. That's where all new features and bug fixes go for testing before a planned release.  The `master` branch should be kept stable at all times.
- Larger changes should be done in separate feature branches.  Make sure to merge `next` into your feature branch, then PR the feature branch to merge into `next`.
- If you break `next` or `master`, fix it (with help if necessary). It's best to run a full test build (i.e. `vagrant destroy`, `vagrant up`) and make sure tools ard targets are working before pushing changes.

## Production VM Notes:
Once you load the VM, unless this was a AWS Workspace install the username and password are:

- Username: samurai
- Password: samurai

The menus are available in the top-left corner of the desktop.

Once you log in, there are a couple of things that might need to be adjusted manually.

## Virtualbox Display
- To automatically adjust the display resolution, do the following:
	- Select Virtualbox `Menu -> View`
	- Click Auto-Resize Guest Display
	- Resize Virtualbox window and display should change to fit window size.
	- OR: Use the `Menu -> View -> Virtual Screen 1` menu to adjust the screen dimensions (e.g. Resize to 1440x900; Scale to 200%). 

# License
The scripts and resources belonging directly to this project are licensed under the Lesser GNU Public License version 3 (LGPLv3).
All software loaded into the VM, including the tools, targets, utilities, and operating system itself retain their original license agreements.


# Contributors
Contributors are very welcome and the contribution process is standard:

  * fork this project
  * make your contribution
  * submit a pull request
  
Substantial or *Regular* contributors may also be brought in as full team members. This includes those who have made substantial contributions to previous versions of SamuraiWTF with the assumption they will continue to do so.

[samurai-slack-url]: https://professionallyevil.slack.com/messages/samuraiwtf
[samurai-katana-url]: https://github.com/SamuraiWTF/katana