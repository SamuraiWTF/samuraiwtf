# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

#shared settings
  config.vm.box = "bento/ubuntu-18.04"
  
  #Do some magic stuff so vagrant uses the right mount command
  config.vm.synced_folder "./config", "/tmp/config", type: "smb"#, mount_options: ["vers=3.02","mfsymlinks","dir_mode=0775","file_mode=0774","sec=ntlm"]
  config.vm.synced_folder ".", "/vagrant", type: "smb"#, mount_options: ["vers=3.02","mfsymlinks","dir_mode=0775","file_mode=0774","sec=ntlm"]

# Single Machine
# Primary build
  config.vm.define "samuraiwtf", primary: true do |samuraiwtf|
    samuraiwtf.vm.host_name = "SamuraiWTF"

    samuraiwtf.vm.provider "hyperv" do |hv|
	  hv.vmname = "SamuraiWTF-4.0RC1"
    # Customize the amount of memory on the VM:
      hv.memory = "2048" 
	  hv.maxmemory = "4096" 
	  hv.cpus = "2" 
	  hv.vm_integration_services = {
		 guest_service_interface: true,
		 heartbeat: true,
		 key_value_pair_exchange: true,
		 shutdown: true,
		 time_synchronization: true,
		 vss: true
	  }
      samuraiwtf.vm.provision :shell, path: "install/hyper-v_provisioning_18.04.sh"
      samuraiwtf.vm.provision :shell, inline: "shutdown -r +1"
    end

    #apply missing patches
	samuraiwtf.vm.provision :shell, path: "install/apt_updates.sh"
	#reboot after upgrading
	samuraiwtf.vm.provision :reload
	samuraiwtf.vm.provision :shell, path: "install/shared_before_Ubuntu.sh"
    samuraiwtf.vm.provision :shell, path: "install/userenv_bootstrap.sh"
    samuraiwtf.vm.provision :shell, path: "install/target_bootstrap.sh"
    samuraiwtf.vm.provision :shell, path: "install/local_targets.sh"

  end

  # forwarded port mapping
  # currently none

  # Private network
  # currently none



  # Provider-specific configuration


end
