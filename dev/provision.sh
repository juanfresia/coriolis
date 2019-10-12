#! /bin/bash

set -ex

apt-get update

# install mongo
#curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
#tar -zxvf mongodb-linux-x86_64-ubuntu1604-3.6.12.tgz
#mkdir -p mongodb
#cp -R -n mongodb-linux-x86_64-ubuntu1604-3.6.12/ mongodb
#echo "export PATH=/home/vagrant/mongodb/mongodb-linux-x86_64-ubuntu1604-3.6.12/bin:$PATH" >> .bashrc
#echo "mongod > /dev/null &" >> .bashrc
#sudo mkdir -p /data/db
#sudo chmod 0777 /data/db/

/vagrant/dev/scripts/install-docker
/vagrant/dev/scripts/install-antlr

curl https://sh.rustup.rs -sSf | sh -s -- -y;

apt-get install -y python3-pip valgrind
pip3 install virtualenv

cd /vagrant && virtualenv venv
source /vagrant/venv/bin/activate && pip3 install -r /vagrant/requirements.txt
