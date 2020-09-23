# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

#shared settings
  config.vm.box = "SamuraiWTF/samuraiwtf-base_box"

#  config.vm.synced_folder "./config", "/tmp/config"

# Single Machine
# Primary build
  config.vm.define "samuraiwtf", primary: true do |samuraiwtf|
    samuraiwtf.vm.host_name = "SamuraiWTF"    

    samuraiwtf.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
      vb.gui = true
      vb.name = "SamuraiWTF-5.0"
    # Customize the amount of memory on the VM:
      vb.memory = "4096"
      vb.customize ["modifyvm", :id, "--vram", "128"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]
      vb.customize ["modifyvm", :id, "--vrde", "off"]
      vb.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
      vb.customize ["modifyvm", :id, "--accelerate2dvideo", "on"]

      config.vm.network "private_network", :type => 'dhcp', :adapter => 2
    end

    samuraiwtf.vm.provision "shell", path: "provision.sh"

    # Make sure VBGuestAdditions is up-to-date and certain pre-requisite packages are installed.  Then restart (reload) so we are using the right
    # version of VBGuestAdditions before continuing.
#     samuraiwtf.vm.provision :shell, inline: "apt-get update && apt-get -y install aufs-tools cgroupfs-mount mate-desktop-environment lightdm python3-pip ansible"
#     # samuraiwtf.vm.provision :reload
#
#     samuraiwtf.vm.provision "ansible_local", run: "once" do |ansible1|
#       ansible1.playbook = "install/samuraiwtf.yml"
#       ansible1.version = "latest"
#       ansible1.extra_vars = { ansible_python_interpreter:"/usr/bin/python3" }
#       ansible1.install_mode = "pip3"
#       ansible1.compatibility_mode = "2.0"
#     end

  end
end
