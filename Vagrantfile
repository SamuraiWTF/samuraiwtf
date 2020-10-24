# -*- mode: ruby -*-
# vi: set ft=ruby :

vagrant_arg = ARGV[0]

Vagrant.configure("2") do |config|
    #set up classes and variables to ask the user which bundle to run
    class BundleQuestion
        def to_s
            names = []
            names << "base"
            print "                                      \n"
            print "                                      \n"
            print "Which bundle would you like to run?\n"
            print "------------------------------------\n"
            print "                                      \n"
            Dir.glob("bundles/*.sh")  {|bundleNames|
                tmp = bundleNames.sub(/^bundles\//, '')
                name = tmp.sub(/\.sh/, '')
                names << name
                puts name
            }
            print "                                      \n"
            print "------------------------------------\n"
            print "Enter base or press return if you would like a base image."
            print "                                      \n"
            print "Bundle: "
            entry = STDIN.gets.chomp

            # default to "base"
            entry = "base" if entry.nil? || entry.empty?

            # Check to ensure that the entry is in the list
            if !names.include? entry then
                print "Bundle doesn't exist!"
                exit
            end
            return entry
        end
    end

#shared settings
  config.vm.box = "SamuraiWTF/samuraiwtf-base_box"

# Primary build
  config.vm.define "samuraiwtf", primary: true do |samuraiwtf|
    samuraiwtf.vm.host_name = "SamuraiWTF"    

    samuraiwtf.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
      vb.gui = true
      vb.name = "SamuraiWTF-5.0.1"

      # Customize the amount of memory on the VM:
      vb.memory = "4096"
      vb.customize ["modifyvm", :id, "--vram", "128"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]
      vb.customize ["modifyvm", :id, "--vrde", "off"]
      vb.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
      vb.customize ["modifyvm", :id, "--accelerate2dvideo", "on"]

      config.vm.network "private_network", :type => 'dhcp', :adapter => 2
    end

    if vagrant_arg == "up" or vagrant_arg == "provision"
        bundle = BundleQuestion.new
    end

    samuraiwtf.vm.provision "shell", path: "provision.sh", :args => bundle.to_s
  end
end
