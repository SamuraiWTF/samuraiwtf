# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

#shared settings
  config.vm.box = "bento/debian-8.7"

  config.vm.synced_folder "./config", "/tmp/config"

#attack machine
  config.vm.define "userenv" do |userenv|
    userenv.vm.host_name = "samuraiwtf"

    userenv.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
      vb.gui = true
      vb.name = "SamuraiWTF"
    # Customize the amount of memory on the VM:
      vb.memory = "2048"
      vb.customize ["modifyvm", :id, "--vram", "16"]
    end

    userenv.vm.provision :shell, path: "install/userenv_bootstrap.sh"
  end

#target server
  config.vm.define "target" do |target|
    target.vm.host_name = "samuraitargets"
    #for debugging mainly
    target.vm.network "private_network", ip: "192.168.42.42"
    target.vm.hostname = "samurai-wtf"
    config.hostsupdater.aliases = ["juice-shop.wtf","dojo-basic.wtf"]

    target.vm.provider "virtualbox" do |vb|
      vb.name = "Samurai Target Server"
      vb.memory = "2048"
    end

    target.vm.provision :shell, path: "install/target_bootstrap.sh"
  end

  # forwarded port mapping
  # currently none

  # Private network
  # currently none



  # Provider-specific configuration


end
