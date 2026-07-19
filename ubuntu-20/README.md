# Choose a Provider
We use Vagrant to build this VM, so that is the prerequisite. Hyper-V is the default provider because most people using SamuraiWTF are doing so from a Windows host and Hyper-V tends to go considerably smoother than other vagrant providers on Windows. This version of SamuraiWTF is built on top of the [_bento/ubuntu-20.04_ base box](https://app.vagrantup.com/bento/boxes/ubuntu-20.04) ,which supports additional providers. We have a configuration for virtualbox but if you need a different provider (e.g. vmware_fusion) then it may be possible by adding its configuration to the Vagrant file in this folder.

## Hyper-V (Default, Windows)
1. From an Administrator PowerShell window, navigate to this folder and run `vagrant up`
2. Select the _Default Switch_ when prompted to select which switch to use. If you don't have a _Default Switch_ option then you will need to create or use a switch that will allow the VM to access the Internet.
3. Wait for the script to complete. This may take a long time (20-30 minutes).
4. Run `vagrant reload` to restart the VM and ensure all the configuration is in place during boot.
5. Connect to the VM and login in with user: _samurai_ , password: _samurai_ 

## VirtualBox
1. From the command line, navigate to this folder and run `vagrant up --provider=virtualbox`
2. The VirtualBox provider will automatically open a new window. Ignore that window for now and wait for the script to complete. This may take a long time (20-30 minutes, possibly longer when running alongside Hyper-V).
3. Run `vagrant reload` to restart the VM and ensure all the configuration is in place during boot.
4. Connect to the VM and login in with user: _samurai_ , password: _samurai_

## VMware Workstation
1. To allow vagrant to modify VMware workstation install the plugin [HERE](https://developer.hashicorp.com/vagrant/docs/providers/vmware/vagrant-vmware-utility) or with Chocolatey `choco install vagrant-vmware-utility`
2. To install VMware provider to [Vagrant](https://developer.hashicorp.com/vagrant/docs/providers/vmware/installation) use the following command `vagrant plugin install vagrant-vmware-desktop` 
3. From the command line, navigate to this folder and run `vagrant up --provider=vmware_desktop`
4. The VMware provider will automatically open a new window/vm in vmware workstation. Ignore that window for now and wait for the script to complete. This may take a long time (20-30 minutes, possibly longer when running alongside Hyper-V).
5. Run `vagrant reload` to restart the VM and ensure all the configuration is in place during boot.
6. Connect to the VM and login in with user: _samurai_ , password: _samurai_

# Final Setup
If you intend to make this VM available to others, for example as a lab environment for a class, there are a few other recommended steps:

- From the command line, run `gnome-tweaks`, navigate to _Extensions_ and enable the _Applications menu_ option. Also enable the _Window list_ option. (_note: if you don't see the Extensions menu option, try closing gnome-tweaks, resizing your window, and opening it again)_.
- In firefox, visit `about:preferences#privacy` and select appropriate options. Since this is going to be used to practice penetration testing, it may be preferable to disable features that may interfere such as block content and popup windows.
- On the same page in firefox, scroll down to Certificates, uncheck the _Query OCSP_ option, and click _View Certificates_. Click the import button and navigate to and open `/etc/samurai.d/certs/localRootCA.crt`. Check the box _Trust this CA to identify websites._ and click the _OK_ button.
- Now on a second tab visit `https://katana.test:8443`. You should see the Katana dashboard. You can set this as the default Homepage in _Settings-->Home_.
- Although the interface can be used to install applications, the command line provides better feedback and error messages. Use katana to install each of the tools and targets you need.  The following example set is a good start for most (note: katana always runs as root):
```bash
katana install zap
katana install wordlists
katana install sqlmap
katana install juice-shop
katana install wayfarer
katana install samurai-dojo
katana install musashi
```

There is also a convenience shell script at `/vagrant/ubuntu-20/install_recommended.sh` that will install all of this plus a few other recommended targets and tools.

- Test that all the targets and tools start as expected before moving on to the final steps.
- Run `katana lock` to freeze the set of targets and tools displayed in the katana UI. Note that a restart (i.e. `katana stop katana && katana start katana`) is needed to see the changes.
- Remove the vagrant user with the command `sudo userdel vagrant` and to save some space you can also remove the working vagrant folder with `sudo rm -rf /vagrant`.
-  **Optional**: If you want to minimize the final size of the image, use a tool such as bleachbit (i.e. `sudo apt install bleachbit`, run with sudo).

## Prepare for Distribution
If you are distributing your image (e.g. for a class), you will want to put it in a suitable format for download / USB storage and importing into Hyper-V.  To do this, perform the following steps:
- Shut down the VM
- Export the VM from HyperV
- Find the vhdx file in the Virtual Hard Disks subfolder (it will likely be labeled Ubuntu), rename it if necessary, and zip it up. This is the only file that needs to be distributed for HyperV. 
