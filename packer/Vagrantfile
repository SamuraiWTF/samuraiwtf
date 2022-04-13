# -*- mode: ruby -*-
# vi: set ft=ruby :

$CIRCLECI=<<SCRIPT
tee "/etc/profile.d/circleci.sh">"/dev/null"<<EOF
# packet info
export PACKET_API_KEY="#{ENV['PACKET_API_KEY']}"
export PACKET_PROJECT_UUID="#{ENV['PACKET_PROJECT_UUID']}"

# vagrant cloud info
export VAGRANT_CLOUD_USER="#{ENV['VAGRANT_CLOUD_USER']}"
export VAGRANT_CLOUD_TOKEN="#{ENV['VAGRANT_CLOUD_TOKEN']}" 

# versioning for vagrant cloud
export MAJOR_RELEASE_VERSION=0
export MINOR_RELEASE_VERSION=0

# text info
export PERSONAL_NUM="#{ENV['PERSONAL_NUM']}"
export TEXTBELT_KEY="#{ENV['TEXTBELT_KEY']}"
EOF
SCRIPT

Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-20.04"
  config.vbguest.auto_update = false
  config.vm.provision "shell", inline: "echo '/vagrant/scripts/setup/prov.sh' >> ~vagrant/.bashrc"
  config.vm.provision "shell", inline: $CIRCLECI # , run:"always"
end
