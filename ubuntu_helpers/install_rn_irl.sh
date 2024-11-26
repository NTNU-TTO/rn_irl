#!/bin/bash

# Install some basics.
apt install sqlite3
apt install python3-venv
apt install python-is-python3

# Set up a common rn_irl group for users.
groupadd -g 99 rn_irl

# Fetch source code
git clone https://github.com/NTNU-TTO/rn_irl
chown root:rn_irl -R rn_irl

# Set up persistent python environment to run in
python -m venv /etc/rn_irl
chown root:rn_irl -R rn_irl
source /etc/rn_irl/bin/activate

# Install required python modules.
pip install streamlit
pip install bcrypt
pip install numpy
pip install scipy
pip install matplotlib
pip install sqlalchemy

# Move the source code inside the virtual python environment.
mv rn_irl /etc/rn_irl/bin

# Move the database to a safe location.
mkdir /var/lib/rn_irl
mv /etc/rn_irl/bin/rn_irl/irl.sdb /var/lib/rn_irl

# Update default database path.
sed -i -e "s#db_path = 'sqlite:///irl.sdb'#db_path = 'sqlite:////var//lib//rn_irl//irl.sdb'#g" /etc/rn_irl/bin/rn_irl/.streamlit/secrets.toml

# Create symlink for executable
chmod ug+x /etc/rn_irl/bin/rn_irl/ubuntu_helpers/*.sh
ln -sf /etc/rn_irl/bin/rn_irl/ubuntu_helpers/rn_irl.sh /bin/rn_irl

# Copy service
cp /etc/rn_irl/bin/rn_irl/ubuntu_helpers/rn_irl.service /lib/systemd/system/

#Reload, enable and run service
systemctl daemon-reload
systemctl enable rn_irl
service rn_irl start
