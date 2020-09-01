#!/usr/bin/bash

echo "Vagrant Provisioning for Ubuntu"

apt install -y python-is-python3

chown samurai:samurai /opt/katana

echo "Installing Katana launcher..."
rm -rf /usr/bin/katana
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
  sudo chown -R root:root /opt/katana
  pushd /opt/katana
  pip install -r requirements.txt
  popd
  popd
  echo "Update is complete."
else
  cd /opt/katana
  sudo python3 ./katanacli.py "\$@"
fi
EOT
chmod 777 /usr/bin/katana

su -c "/usr/bin/katana --update"