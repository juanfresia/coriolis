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

 
  config.vm.provision 'shell', privileged: false, inline: <<-SHELL
    sudo apt-get update
    curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
    tar -zxvf mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
    mkdir -p mongodb
    cp -R -n mongodb-linux-x86_64-ubuntu1604-3.6.12/ mongodb
    echo "export PATH=/home/vagrant/mongodb/mongodb-linux-x86_64-ubuntu1604-3.6.12/bin:$PATH" >> .bashrc
    echo "mongod > /dev/null &" >> .bashrc
    sudo mkdir -p /data/db
    sudo chmod 0777 /data/db/

    sudo apt-get install -y openjdk-8-jre-headless openjdk-8-jdk
    wget http://www.antlr.org/download/antlr-4.7.1-complete.jar
    sudo cp antlr-4.7.1-complete.jar /usr/local/lib/
    echo "export CLASSPATH=.:/usr/local/lib/antlr-4.7.1-complete.jar:$CLASSPATH" >> .bashrc
    echo "alias antlr4='java -Xmx500M -cp "/usr/local/lib/antlr-4.7.1-complete.jar:$CLASSPATH" org.antlr.v4.Tool'" >> .bashrc
    echo "alias grun='java org.antlr.v4.gui.TestRig'" >> .bashrc

    curl https://sh.rustup.rs -sSf | sh -s -- -y;

    sudo apt-get install -y python3-pip valgrind
    sudo pip3 install virtualenv
    cd /vagrant && virtualenv venv
    source /vagrant/venv/bin/activate && pip3 install -r /vagrant/requirements.txt && deactivate
    SHELL

  end
end
