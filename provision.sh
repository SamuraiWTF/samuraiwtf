#!/usr/bin/bash

echo "Vagrant Provisioning for Ubuntu"

apt install -y python-is-python3 gnome-shell-extension-arc-menu gnome-tweaks

chown samurai:samurai /opt/katana

cp /vagrant/base/common/*.png /opt/samurai/
cp /vagrant/base/common/*.jpg /opt/samurai/

echo "Setting up first-time login script."
rm -f /etc/profile.d/first_login.sh
cat <<EOT >> /etc/profile.d/first_login.sh
#!/bin/bash

if [ -e ~/.samurai ]
then
  echo "Skipping first run: already run first time scripts."
else
  cd /etc/dconf
  /usr/bin/dconf write /org/mate/desktop/background/picture-filename "'/opt/samurai/samurai_wallpaper_wide_fade.jpg'"
  /usr/bin/dconf write /org/mate/desktop/background/picture-options "'stretched'"
  /usr/bin/dconf write /org/gnome/desktop/background/picture-uri "'file:///opt/samurai/samurai_wallpaper_wide_fade.jpg'"
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

echo "Installing Katana launcher..."
rm -f /usr/bin/katana
cat <<EOT >> /usr/bin/katana
#!/usr/bin/bash
if [[ "\$1" = "--update" ]]; then
  echo "Updating Katana..."
  sudo rm -rf /tmp/katana
  pushd /tmp
  sudo rm -rf /tmp/katana
  sudo git clone --depth=1 --single-branch --branch "master" https://github.com/SamuraiWTF/katana.git || exit
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