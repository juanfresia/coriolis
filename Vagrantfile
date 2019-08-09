# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |vb|
    vb.customize ['modifyvm', :id, '--nictype1', 'virtio']
    vb.memory = 1024
    vb.cpus = 2
    vb.linked_clone = true
  end

  config.vm.define "Concutest" do |box|
    box.vm.network "private_network", ip: "10.0.0.2"
    box.vm.hostname = "Concutest"

    box.vm.provider "virtualbox" do |vb|
      vb.name = "Concutest"
    end

 
  config.vm.provision 'shell', privileged: false, inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install valgrind
    curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
    tar -zxvf mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
    mkdir -p mongodb
    cp -R -n mongodb-linux-x86_64-ubuntu1604-3.6.12/ mongodb
    echo "export PATH=/home/vagrant/mongodb/mongodb-linux-x86_64-ubuntu1604-3.6.12/bin:$PATH" >> .bashrc
    sudo mkdir -p /data/db
    sudo chmod 0777 /data/db/

    SHELL

  end
end
