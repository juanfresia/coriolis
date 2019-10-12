#! /bin/bash

set -ex

apt-get update

/vagrant/dev/scripts/install-docker
/vagrant/dev/scripts/install-antlr

curl https://sh.rustup.rs -sSf | sh -s -- -y;

cp /vagrant/dev/files/mongodb.service /etc/systemd/system/mongodb.service
systemctl enable mongodb

apt-get install -y python3-pip valgrind
pip3 install virtualenv

cd /vagrant && virtualenv venv
source /vagrant/venv/bin/activate && pip3 install -r /vagrant/requirements.txt
