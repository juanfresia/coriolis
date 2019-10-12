# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |vb|
    vb.customize ['modifyvm', :id, '--nictype1', 'virtio']
    vb.memory = 4096
    vb.cpus = 2
    vb.linked_clone = true
  end

  config.vm.define "Concutest" do |box|
    box.vm.network "private_network", ip: "10.0.0.2"
    box.vm.hostname = "Concutest"

    box.vm.provider "virtualbox" do |vb|
      vb.name = "Concutest"
    end
  end

  config.vm.provision 'shell' do |s|
    s.privileged = true
    s.path = "dev/provision.sh"
  end
end
