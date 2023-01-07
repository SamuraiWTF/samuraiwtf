<p align="center">
  <img alt="SamuraiWTF Logo" src="http://tiny.si/images/owasp_samurai_v3.png"  height="400"/>
</p>

## Samurai Web Training Framework 5.2

<p align="center">
  <a href="https://github.com/SamuraiWTF/samuraiwtf/releases"> <img alt="Github" src="https://img.shields.io/github/downloads/SamuraiWTF/samuraiwtf/total.svg?label=Github%20Downloads"/></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf"> <img alt="SourceForge" src="https://img.shields.io/sourceforge/dt/samurai.svg?label=%28Deprecated%29%20%20SourceForge%20Downloads"/></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf/releases"> <img alt="Latest version" src="https://img.shields.io/github/release/SamuraiWTF/samuraiwtf.svg" /></a>
  <a href="https://github.com/SamuraiWTF/samuraiwtf/blob/master/LICENSE" > <img alt="License" src="https://img.shields.io/badge/license-GPLv3-blue.svg" /></a> 
</p>

----

This project is not a vulnerable application. It is a framework designed for quickly configuring training virtual machines with tools and vulnerable application targets. 
For example, an instructor could use SamuraiWTF to easily set up a virtual machine image containing OWASP ZAP and OWASP Juice Shop, and then distribute it to each student as a training lab environment.

This project includes and uses the [Samurai Katana][samurai-katana-url] project to manage installation and running of tools and targets in the virtual environment. 

**Reference Implementation**
Currently the reference implementation for this project is built on top of Ubuntu 20.04 (look in the ubuntu-20 subfolder).

**Want to chat with us? Join us in either the OWASP Slack #project-samuraiwtf channel.**

**Want to Contribute? See [here](#Contributors)**

**Art Credit:** the above Samurai figure is the original work of Ben Faircloth, who has granted the OWASP SamuraiWTF project permission to use in the product and websites. 

## How to set up Samurai WTF
There are several options available to you. The quickest option is to download a pre-built virtual machine and then use Katana (already installed) to configure it with the targets you want to use.

### Option 1: Download Pre-Built OVA (for Oracle VirtualBox)
This option works best if you are not using Windows, or if you are using Windows without Hyper-V running.

[Download SamuraiWTF for VirtualBox](https://downloads-samuraiwtf-com.s3.us-west-2.amazonaws.com/SamuraiWTF.ova)
* MD5: `edbcb6dd46d31ad2ca7a813520eee7e4`
* SHA256: `f43d4c59bd49f032b5ae3b70a165398fa8dee68c88336c918c7b25f0ed633044`

For more information on removing or disabling Hyper-V, see [these instructions from Microsoft](https://support.microsoft.com/en-us/help/3204980/virtualization-applications-do-not-work-together-with-hyper-v-device-g).

### Option 2: Download Pre-Built VHDX (for Hyper-V)
This option works best if you are running Windows 10 or higher and already have Hyper-V installed. If you use the Windows Linux Subsystem (WLS), then you have Hyper-V installed.

[Download SamuraiWTF for Hyper-V](https://downloads-samuraiwtf-com.s3.us-west-2.amazonaws.com/SamuraiWTF_HyperV.zip)
* MD5: `93d262417fc0dd3a16c96b516be60d2e`
* SHA256: `d4aad0a92f94604e082f02b3247e9a1a1406aaad85f2c1114f2ae253cc5627fe`

Once it is downloaded, you will want to unzip the file and then create a new VM in Hyper-V. Attach the .hvdx drive and set the RAM to 4096.

### Option 3: Build an Amazon Workspace
This option works best if you are familiar with Amazon Web Services (AWS) and want your students to remote into the lab environments instead of running them as local virtual machines. This can be a great option when students are running potentially low-powered machines because it even works from a Chromebook. For details, view [/amazon-linux/README.md](https://github.com/SamuraiWTF/samuraiwtf/blob/main/amazon-linux/README.md).

### Build on Hyper-V or VirtualBox with Vagrant
Currently, the most stable Vagrant build is the one for Ubuntu 20.04.  Details are in the file [/amazon-linux/README.md](https://github.com/SamuraiWTF/samuraiwtf/blob/main/ubuntu-20/README.md).

## Default Password
There is a default user and password for the SamuraiWTF environment: `samurai` / `samurai`
This is the same for every build except the AWS Workspace, where you will instead use your workspace username and password.

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


- Our integration branch is the one called `next`. That's where all new features and bug fixes go for testing before a planned release.  The `main` branch should be kept stable at all times.
- Larger changes should be done in separate feature branches.  Make sure to merge `next` into your feature branch, then PR the feature branch to merge into `next`.
- If you break `next` or `main`, fix it (with help if necessary). It's best to run a full test build (i.e. `vagrant destroy`, `vagrant up`) and make sure tools ard targets are working before pushing changes.

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

[samurai-katana-url]: https://github.com/SamuraiWTF/katana
