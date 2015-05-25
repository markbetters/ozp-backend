#!/bin/bash

################################################################################
#	Script largely taken from https://gist.github.com/hangtwenty/5546945
#	Modified to use the latest versions of Python 2.7, virtualenv, virtualenvwrapper
#
# 	Necessary because Centos 6 ships with Python 2.6, and replacing the system
#	version of Python with something else causes very bad things
################################################################################

HOME_DIR=/home/vagrant
# Source: http://toomuchdata.com/2012/06/25/how-to-install-python-2-7-3-on-centos-6-2/

# Install stuff #
#################
cd ${HOME_DIR}
# Install development tools and some misc. necessary packages
sudo yum -y groupinstall "Development tools"
sudo yum -y install zlib-devel  # gen'l reqs
sudo yum -y install bzip2-devel openssl-devel ncurses-devel  # gen'l reqs
# yum -y install mysql-devel  # req'd to use MySQL with python ('mysql-python' package)
sudo yum -y install libxml2-devel libxslt-devel  # req'd by python package 'lxml'
sudo yum -y install unixODBC-devel  # req'd by python package 'pyodbc'
sudo yum -y install sqlite sqlite-devel  # you will be sad if you don't install this before compiling python, and later need it.
# Alias shasum to == sha1sum (will prevent some people's scripts from breaking)
echo 'alias shasum="sha1sum"' >> $HOME/.bashrc

# Install Python 2.7.4 (do NOT remove 2.6, by the way)
wget --no-check-certificate https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar xf Python-2.7.9.tgz
cd Python-2.7.9
./configure --prefix=/usr/local
make
sudo make altinstall
cd ..

# Install Python 3.4.3
wget --no-check-certificate https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
tar xf Python-3.4.3.tgz
cd Python-3.4.3
./configure --prefix=/usr/local
make
sudo make altinstall
cd ..

# Install virtualenv and virtualenvwrapper
# Once you make your first virtualenv, you'll have 'pip' in there.
# I got bitten by trying to install a system-wide (i.e. Python 2.6) version of pip;
# it was clobbering my access to pip from within virtualenvs, and it was frustrating.
# So these commands will install virtualenv/virtualenvwrapper the old school way,
# just so you can make yourself a virtualenv, with pip, and then do everything Python-related
# that you need to do, from in there.

wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.1.1.tar.gz#md5=901ecbf302f5de9fdb31d843290b7217
tar -xvzf virtualenv-12.1.1.tar.gz
cd virtualenv-12.1.1/
sudo python setup.py install
cd ..
# install setuptools
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
# install pip (will this cause a problem?)
wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
# install virtualenvwrapper
wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenvwrapper/virtualenvwrapper-4.5.1.tar.gz#md5=5ff62b23d051767d351484db2c1fcb75
tar -xvzf virtualenvwrapper-*
cd virtualenvwrapper-4.5.1/
sudo python setup.py install
cd ..
echo 'export WORKON_HOME=~/Envs' >> .bashrc # Change this directory if you don't like it
source $HOME/.bashrc
mkdir -p $WORKON_HOME
echo '. /usr/bin/virtualenvwrapper.sh' >> .bashrc
source $HOME/.bashrc

# Done!
# Now you can do: `mkvirtualenv foo --python=python2.7`

# Extra stuff #
###############

# These items are not required, but I recommend them

# Add RPMForge repo
sudo yum -y install http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.i686.rpm
