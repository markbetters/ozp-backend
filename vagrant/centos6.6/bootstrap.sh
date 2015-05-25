#!/usr/bin/env bash

# initial box configuration
source /vagrant/initial_provisioning.sh | tee /home/vagrant/initial_provisioning.log

# install python2.7 and python3.4.3 and associated tools
source /vagrant/update_python.sh | tee /home/vagrant/update_python.log

# build ozp apps
#source /vagrant/build.sh | tee /home/vagrant/build.log

# package ozp apps
#source /vagrant/package.sh | tee /home/vagrant/package.log

# deploy ozp apps
#source /vagrant/deploy.sh | tee /home/vagrant/deploy.log
