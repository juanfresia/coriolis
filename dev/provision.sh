#! /bin/bash

set -ex

apt-get update

/vagrant/dev/scripts/install-docker
/vagrant/dev/scripts/install-antlr
/vagrant/dev/scripts/install-rust

# Set up MongoDB as a container ran with systemd
cp /vagrant/dev/files/mongodb.service /etc/systemd/system/mongodb.service
systemctl enable mongodb

apt-get install -y python3-pip valgrind
pip3 install virtualenv

cd /vagrant/coriolis && virtualenv venv
source /vagrant/coriolis/venv/bin/activate && pip3 install -r /vagrant/coriolis/requirements.txt
