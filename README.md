# samuraiwtf

*NOTE: This project should currently be considered experimentation only, as it is not yet ready for release.*

The purpose behind this project is to migrate the SamuraiWTF (http://www.samura-wtf.org) distribution to a standalone Debian package structure for easier maintenance and installation flexibility.  SamuraiWTF is intended to be installed over a Ubuntu distro, though this may be expanded in the future.

## Building the Package
In general, the package can be built with dpkg as follows:
```
dpkg -b samurai-wtf samurai-wtf-0.0.0_i386.deb
```
... where the 0.0.0 is replaced with the actual release version of the distribution.  Note that from a vanilla installation of Ubuntu some Debian build dependencies may be required in order to do this (we'll update this page once we work those out exactly).

## Installing the Package
There are a few possible ways to do this, but the simplest is probably:
```
gdebi samurai-wtf-0.0.0_i386.deb
```
...and again, the 0.0.0 refers to the actual release version of the distribution.
