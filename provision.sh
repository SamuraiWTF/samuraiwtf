#!/usr/bin/bash

echo "Vagrant Provisioning for Ubuntu"

echo "Command line"
bundle=$1



apt install -y python-is-python3 gnome-shell-extension-arc-menu gnome-tweaks

chown samurai:samurai /opt/katana

cp /vagrant/base/common/*.png /opt/samurai/
cp /vagrant/base/common/*.jpg /opt/samurai/

sed -i 's/^Categories=.*/&samuraiwtf;/' /usr/share/applications/mate-terminal.desktop
# TODO: remove /vagrant entry from /etc/fstab

echo "Setting up first-time login script."
rm -f /etc/profile.d/first_login.sh
cat <<EOT >> /etc/profile.d/first_login.sh
#!/bin/bash

if [ -e ~/.samurai ]
then
  echo "Skipping first run: already run first time scripts."
else
  cd /etc/dconf
  /usr/bin/dconf write /org/mate/desktop/background/picture-filename "'/opt/samurai/samurai-wide-faded.jpg'"
  /usr/bin/dconf write /org/mate/desktop/background/picture-options "'stretched'"
  /usr/bin/dconf write /org/gnome/desktop/background/picture-uri "'file:///opt/samurai/samurai-wide-faded.jpg'"
  /usr/bin/dconf write /org/gnome/desktop/screensaver/picture-uri "'file:///opt/samurai/samurai-wide-faded.jpg'"
  /usr/bin/dconf write /org/gnome/desktop/session/idle-delay "uint32 0"
  /usr/bin/dconf write /org/gnome/settings-daemon/plugins/power/sleep-inactive-ac-type "'nothing'"
  /usr/bin/dconf write /org/gnome/settings-daemon/plugins/power/sleep-inactive-battery-type "'nothing'"
  /usr/bin/dconf write /org/mate/terminal/profiles/default/custom-command "'bash'"
  /usr/bin/dconf write /org/mate/terminal/profiles/default/use-custom-command true
  /usr/bin/dconf write /org/gnome/shell/enabled-extensions "['arc-menu@linxgem33.com']"
  /usr/bin/dconf write /org/gnome/shell/extensions/arc-menu/dtp-dtd-state "[false, false]"
  /usr/bin/dconf write /org/gnome/mutter/overlay-key "'Super_L'"
  /usr/bin/dconf write /org/gnome/desktop/wm/keybindings/panel-main-menu "['<Alt>F1']"
  /usr/bin/dconf write /org/gnome/shell/extensions/arc-menu/menu-button-appearance "'Text'"
  /usr/bin/dconf write /org/gnome/shell/extensions/arc-menu/enable-pinned-apps false

  if [ ! -L ~/samurai ]; then
    ln -s /opt/samurai ~/samurai
  fi
  touch ~/.samurai

fi
EOT

echo "Setting up distribution prep file /tmp/prepare-for-distribution.sh"
cat <<EOT >> /usr/bin/prepare-for-distribution.sh
#!/usr/bin/bash
sudo userdel vagrant
sudo apt install -y bleachbit
sudo bleachbit -c apt.* system.trash system.rotated_logs system.tmp
sudo bleachbit -w -o /opt/ /var/ /etc/ /tmp/ /home/
sudo apt remove -y bleachbit
echo "***********  DONE  ***********"
echo "* 1) you might want to do a 'katana lock'. This will make the katana UI a bit more student-friendly."
echo "* 2) Don't forget to remove the /vagrant share from /etc/fstab and the VM configuration."
echo "* 3) Shutdown, double-check your VM settings, then export your .OVI file."
EOT

chmod a+x /usr/bin/prepare-for-distribution.sh

echo "Installing Katana launcher..."
rm -f /usr/bin/katana
cat <<EOT >> /usr/bin/katana
#!/usr/bin/bash
if [[ "\$1" = "--update" ]]; then
  echo "Updating Katana..."
  BRANCH="master"
  if [[ -n "\$2" ]] ; then
    BRANCH="\$2"
  fi
  sudo rm -rf /tmp/katana
  pushd /tmp
  sudo rm -rf /tmp/katana
  echo "Cloning repository branch '\$BRANCH'"
  sudo git clone --depth=1 --single-branch --branch \$BRANCH https://github.com/SamuraiWTF/katana.git || exit
  sudo mkdir -p /opt/katana
  sudo cp -R /tmp/katana/* /opt/katana/
  sudo chown -R samurai:root /opt/katana
  cd /opt/katana
  sudo pip install -r requirements.txt
  popd
  echo "Update is complete."
else
  cd /opt/katana
  sudo python3 ./katanacli.py "\$@"
fi
EOT
chmod 777 /usr/bin/katana

su -c "/usr/bin/katana --update"

katana install katana
katana start katana
systemctl enable samurai-katana

# Run the chosen bundle
echo "Running chosen bundle"
cp /vagrant/bundles/${bundle}.sh /tmp
. /tmp/${bundle}.sh

