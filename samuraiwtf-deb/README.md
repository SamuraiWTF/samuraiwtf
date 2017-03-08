# samuraiwtf

*NOTE: This project should currently be considered experimentation only, as it is not yet ready for release.*

The purpose behind this project is to migrate the SamuraiWTF (http://www.samurai-wtf.org) distribution to a standalone Debian package structure for easier maintenance and installation flexibility.  SamuraiWTF is intended to be installed over a Ubuntu distro, though this may be expanded in the future.

## Pre-Installation
If building from the ground up, create the user "samurai" during installation of the OS. This is, by convention, the default user for SamuraiWTF.

Some packages that may need to be pre-installed:
* kde is the conventional SamuraiWTF desktop environment. Not strictly required, but more familiar.
* git is of course needed if building from this repo.
* gdebi is the easy way to get the debian package installed.

To install these, use:
```
sudo apt-get update
sudo apt-get install kde-plasma-desktop git gdebi
```

## Building the Package
In general, the package can be built with dpkg as follows:
```
git clone https://github.com/SamuraiWTF/samuraiwtf.git
cd samuraiwtf
dpkg -b samurai-wtf samurai-wtf-0.0.0_i386.deb
```
... where the 0.0.0 is replaced with the actual release version of the distribution.  Note that from a vanilla installation of Ubuntu some Debian build dependencies may be required in order to do this (we'll update this page once we work those out exactly).

## Installing the Package
There are a few possible ways to do this, but the simplest is probably:
```
sudo gdebi samurai-wtf-0.0.0_i386.deb
```
...and again, the 0.0.0 refers to the actual release version of the distribution.

## Installation Notes
* You will be prompted to choose a root password when installing MySQL. For now this should be "samurai" (this will be configurable at a later time)
