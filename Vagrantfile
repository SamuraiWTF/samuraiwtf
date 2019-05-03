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
      vb.name = "SamuraiWTF-4.2.0"
    # Customize the amount of memory on the VM:
      vb.memory = "4096"
      vb.customize ["modifyvm", :id, "--vram", "128"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]      

      # samuraiwtf.vbguest.auto_update = false
      # samuraiwtf.vm.provision :shell, inline: "shutdown -r +1"
    end

    samuraiwtf.vm.provision "ansible_local", run: "once" do |ansible1|      
      ansible1.playbook = "install/bootstrap.yml"
      ansible1.version = "latest"
      ansible1.install_mode = "pip"
    end

    samuraiwtf.vm.provision :reload, run: "once" 

    samuraiwtf.vm.provision "ansible_local" do |ansible2|      
      ansible2.playbook = "install/samuraiwtf.yml"
    end
    # samuraiwtf.vm.provision :shell, path: "install/shared_before.sh"
    # samuraiwtf.vm.provision :shell, path: "install/userenv_bootstrap.sh"
    # samuraiwtf.vm.provision :shell, path: "install/target_bootstrap.sh"
    # samuraiwtf.vm.provision :shell, path: "install/local_targets.sh"

  end

#Additional build options.  Sepearate virtual machines
#attack machine
#   config.vm.define "userenv", autostart: false do |userenv|
#     userenv.vm.host_name = "samuraiwtf"

#     userenv.vm.provider "virtualbox" do |vb|
#     # Display the VirtualBox GUI when booting the machine
#       vb.gui = true
#       vb.name = "SamuraiWTF User Environment"
#     # Customize the amount of memory on the VM:
#       vb.memory = "2048"
#       vb.customize ["modifyvm", :id, "--vram", "16"]
#     end

#     userenv.vm.provision :shell, path: "install/shared_before.sh"
#     userenv.vm.provision :shell, path: "install/userenv_bootstrap.sh"
#   end

# #target server
#   config.vm.define "target", autostart: false do |target|
#     target.vm.host_name = "samuraitargets"
#     #for debugging mainly
#     target.vm.network "private_network", ip: "192.168.42.42"
#     target.vm.hostname = "samurai-wtf"
#     #config.hostsupdater.aliases = ["juice-shop.wtf","dojo-basic.wtf"]

#     target.vm.provider "virtualbox" do |vb|
#       vb.name = "Samurai Target Server"
#       vb.memory = "2048"
#     end

#     target.vm.provision :shell, path: "install/shared_before.sh"
#     target.vm.provision :shell, path: "install/target_bootstrap.sh"
#   end

  # forwarded port mapping
  # currently none

  # Private network
  # currently none



  # Provider-specific configuration


end
