# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

#shared settings
  config.vm.box = "bento/debian-9"

#  config.vm.synced_folder "./config", "/tmp/config"

# Single Machine
# Primary build
  config.vm.define "samuraiwtf", primary: true do |samuraiwtf|
    samuraiwtf.vm.host_name = "SamuraiWTF"    

    samuraiwtf.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
      vb.gui = true
      vb.name = "SamuraiWTF-4.2.2"
    # Customize the amount of memory on the VM:
      vb.memory = "4096"
      vb.customize ["modifyvm", :id, "--vram", "128"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]      

      # samuraiwtf.vbguest.auto_update = false
      # samuraiwtf.vm.provision :shell, inline: "shutdown -r +1"
    end

    # Make sure VBGuestAdditions is up-to-date and certain pre-requisite packages are installed.  Then restart (reload) so we are using the right
    # version of VBGuestAdditions before continuing.
    samuraiwtf.vm.provision :shell, inline: "apt-get update && apt-get -y install aufs-tools cgroupfs-mount mate-desktop-environment lightdm python-pip ansible"
    samuraiwtf.vm.provision :reload 

    samuraiwtf.vm.provision "ansible_local", run: "once" do |ansible1|      
      ansible1.playbook = "install/samuraiwtf.yml"
      ansible1.version = "latest"
      ansible1.install_mode = "pip"
      ansible1.compatibility_mode = "2.0"
    end

  end
end
