---
title: SamuraiWTF BaseBox
---

# SamuraiWTF Basebox

The Samurai Web Training Framework is made up of two parts:
* The base OS installation of supporting software packages
* Katana, a web UI and CLI tool for managing tools and targets running within the SamuraiWTF.

The base OS can be any Linux flavor that can meet the requirements below in the _Basebox Requrements_ section of this document.
The reference implementation for the Basebox includes:

* Amazon Linux, specifically the latest version in AWS Workspaces.
* Ubuntu, the latest LTS version (currently 18.04 "Bionic Beaver")

_It should be noted that much of what is done in the following SamuraiWTF Basebox setup is against secure deployment best practices. It is a framework for hosting vulnerable targets. Do not host a SamuraiWTF lab in a network with other live/production systems._

## Basebox Requirements

### Desktop Manager
SamuraiWTF is intended to be a student-friendly lab environment. 
For convenience, a XDG-based solution should be used so that .menu and .directory files can remain consistent across builds.

### Base Software / Packages
 Name    | Notes    
 ------- | -------- 
 nginx | Used primarily as a reverse proxy for many of the tools. Also used as a convenience for locally-hosted payloads.
 curl | Used by supporting scripts.
 docker | This is the preferred target deployment solution.
 docker-compose | Currently required by the Samurai-Dojo targets.
 unzip | Used by supporting scripts. 
 python3 | Including pip3. Required by supporting scripts and Katana.
 php-fpm | Needed as a convenience for the local nginx build.
 nano | Or other simple command-line editor.
 npm 12 | Used for deploying some targets that are not in docker (e.g. Juice-Shop).
 yarn | Used in conjunction with npm
 Java 8 | A Java Runtime 8 or greater is needed to run tools such as Burp Suite and ZAP.
 Ansible | Not strictly required, but a local ansible playbook is a convenient way to manage the _Additional Basebox Steps_ below, so it is needed at least for the reference implenetations.
 
 ### Additional Basebox Steps
 
 Typically these steps are run from a combination of a bash script and locally-run Ansible playbook, but other mechanisms are certainly possible. 
 
 The folder structure under opt should be as follows:
 ```
/opt
  |--- katana  // copy contents from the katana folder in this repo.
  |--- samurai // used as a central location for tools
  |--- targets // used as a central location for targets
```
With this in mind, the installation steps are: 

 1. Install all of the above base required software
 1. There is a default nginx configuration under base/common/config/nginx that can be used in most cases.
 1. Setup the xdg menu framework such that it falls under /etc/samurai.d. An example set of Ansible plays are below under the [_xdg Menu Files_](#xdg-menu-files) heading. 
 1. Copy the .png files from base/common into /opt/samurai
 1. Setup the default nginx service (i.e. on port 80) such that it supports PHP and has a local web root (e.g. /usr/share/nginx/html/).  You can use `<?php phpinfo(); ?>` to check if php is running correctly.
 1. The katana folder for this repo should be copied to /opt/katana.
 1. Make a katana launcher script and put it in /usr/bin/katana.  A recommended script is found below in the [_Katana Launcher_](#katana-launcher) section.
 1. Install the katana/requirements.txt using pip
 1. Install Firefox or Chrome, if it isn't already there, or some derivative (e.g. IceWeasle or Chromium)
 
 #### Katana Launcher
 ```bash
#!/bin/bash
if [[ "$1" = "--update" ]]; then
  sudo rm -rf /tmp/samuraiwtf
  pushd /tmp
  sudo git clone --depth=1 --single-branch --branch "5.0-dev" https://github.com/SamuraiWTF/samuraiwtf.git || exit
  sudo mkdir -p /opt/katana
  sudo cp -R /tmp/samuraiwtf/katana/* /opt/katana/
  popd
else
  cd /opt/katana
  sudo python3 ./katanacli.py "$@"
fi
```
 
 #### xdg Menu Files
 ```yaml
  - name: Setup menu /etc/samurai.d/desktop-directories
    file:
      path: /etc/samurai.d/desktop-directories/
      state: directory
    become: yes

  - name: Setup menu /etc/samurai.d/applications
    file:
      path: /etc/samurai.d/applications/
      state: directory
    become: yes

  - name: Setup menu /etc/samurai.d/desktop-directories
    file:
      path: /etc/samurai.d/desktop-directories/
      state: directory
    become: yes

  - name: Create main samurai-wtf menu
    copy:
      dest: /etc/samurai.d/desktop-directories/samuraiwtf.directory
      content: |
        [Desktop Entry]
        Type=Directory
        Name=Samurai WTF
        Icon=/opt/samurai/samurai-icon.png
      mode: 0744
    become: yes

  - name: Create applications-merged folder
    file:
      path: /etc/xdg/menus/applications-merged
      state: directory
    become: yes

  - name: Create main samurai-wtf menu
    copy:
      dest: /etc/xdg/menus/applications-merged/samuraiwtf.menu
      content: |
        <!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
        "http://www.freedesktop.org/standards/menu-spec/menu-1.0.dtd">
        <Menu>
          <Name>Applications</Name> <!-- This is necessary for your directory to appear in the applications drop down -->
          <Menu> <!--app -->
            <Name>Samurai</Name>
            <AppDir>/etc/samurai.d/applications</AppDir>
            <DirectoryDir>/etc/samurai.d/desktop-directories</DirectoryDir>
            <Directory>samuraiwtf.directory</Directory>
            <Include>
              <Category>samuraiwtf</Category>
            </Include>
          </Menu> <!-- End app -->
        </Menu> <!-- End Applications -->
      mode: 0744
    become: yes
```
 
 ### Optional Steps
 
 These are recommended to polish things up for a class.
 
1. As this is a lab environment, turning on passwordless sudo is convenient.  Add `+:root:ALL` to /etc/security/access.conf
1. Install the FoxyProxy addon in Chrome or Firefox
1. Install katana UI using `katana install katana`, and set katana.wtf as the browser's homepage.
1. Setup the opt/samurai/samurai-background.png image as the desktop background.
1. Use katana to install whatever tools and targets will be needed for the class.