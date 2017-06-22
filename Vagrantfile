# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "bento/debian-8.7"

  config.vm.host_name = "samuraiwtf"

  # forwarded port mapping
  # currently none

  # Private network
  # currently none

config.vm.synced_folder "./config", "/tmp/config"

  # Provider-specific configuration

config.vm.provider "virtualbox" do |vb|
  # Display the VirtualBox GUI when booting the machine
    vb.gui = true
    vb.name = "samuraiwtf"
  # Customize the amount of memory on the VM:
    vb.memory = "2048"
    vb.customize ["modifyvm", :id, "--vram", "16"]
end

  config.vm.provision :shell, path: "install/userenv_bootstrap.sh"
end
