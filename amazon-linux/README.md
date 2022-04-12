# Amazon Linux Notes
The reasoning behind using Amazon Linux 2 as a platform for hosting SamuraiWTF is that AWS Workspaces provides a convenient mechanism for hosting student labs for application security classes.

There are two options for running SamuraiWTF on Amazon Linux 2:

- Run it in an AWS Workspace
- Run it as a local virtual machine

## SamuraiWTF in AWS Workpace
This is convenient for online hosted classrooms because the students need only install the AWS Workspaces client. There is no need for students to configure a hypervisor or to fight with getting a virtual machine environment running. There are some caveats to this build:

  * You must start with an Amazon Linux workspace.  4GB Ram is sufficient.  Disk size can be 20GB or more.
  * AWS terms of services does not allow any hacking / scanning from workspaces. Therefore, if this is an undisciplined group of students, you are encouraged to remove the default outbound rule for the workspaces Security Group once the image is configured. Doing so will prevent outbound traffic from the workspace to the Internet.  Strictly speaking, once SamuraiWTF is installed and configured, internet access outbound should no longer be needed.  All the target apps are contained within the environment as local destinations. In practice, some targets may experience minor timeout issues while attempting to fetch third-party resources.

### Workspace Installation Process
  * Create a Workspace (4+GB Ram, 20+ GB user disk space)
  * Log in, open a terminal, and make sure git is installed by running `git`.  If it is not installed, run `sudo yum install git`.
  * Run the following to pull down and run the build scripts:
```bash
cd ~
git clone https://github.com/SamuraiWTF/samuraiwtf.git
samuraiwtf/amazon-linux/bootstrap.sh
```
  * During the process you may be prompted to input your *BECOME Password*. This is just your user's password and is used to run certain commands as root. Wait for the process to complete.
  * Restart the workspace, open Firefox, and verify that the katana graphical console is visible.
  * From here you can [use Katana](https://github.com/SamuraiWTF/katana) (either through the console or command line) to install tools and targets for the class.

## Use Vagrant to Build Local VM
If you instead want to run a local virtual machine build of SamuraiWTF using a similar setup to AWS Workspaces, you can do so with Vagrant.

For this to work, you will first need to install [Oracle VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Hashicorp Vagrant](https://www.vagrantup.com/). VirtualBox is the only hypervisor for which we have a base box at this time, but you can build it in Virtual Box and then export / import to others such as Hyper-V.

### Local VM Installation Process
  * Open a terminal window
  * Clone this repo `git clone https://github.com/SamuraiWTF/samuraiwtf.git`
  * Navigate to the amazon-linux subfolder with `cd samuraiwtf/amazon-linux`
  * Run `vagrant up` and wait for it to complete. This may take several minutes.
  * Run `vagrant reload` and for the reboot to complete. You should now see a screen to login as the user _samurai_.
  * Login with default password `samurai`.
  * Open firefox, then go into `settings --> security` and use the search bar to find the certificates. Click `View Certificates`  and make sure the _Authorities_ tab is selected. At the bottom of the table you will find an _import_ button. Click that and browse to the file `/etc/samurai.d/certs/rootCACert.pem`. Click the checkbox to trust this certificate for websites and complete the import.
  * Close firefox and open it a second time. Verify that the Katana graphical console is the home page.
  * From here you can [use Katana](https://github.com/SamuraiWTF/katana) (either through the console or command line) to install tools and targets for the class.

### Local VM Troubleshooting
  * This vagrant box installs guest tools, so if you don't like the screen dimensions they can be changed inside the VM using: `System --> Control Center --> Displays`
  * If Firefox doesn't seem to trust the internal targets (like https://katana.test:8443) then double-check that you installed the CA certificate as described in the above section.

