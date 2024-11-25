#!/bin/bash

# Sets up a staging environment for testing bleeding edge RN IRL straight outta github.
cd /etc
# Set up a virtual environment for python
python -m venv rn_irl_staging

# Clone latest'n'greatest to the staging environment.
cd /etc/rn_irl_staging/bin
git clone https://github.com/NTNU-TTO/rn_irl
# Source and install requirements
source /etc/rn_irl_staging/bin/activate
cd /etc/rn_irl_staging
pip install streamlit
pip install bcrypt
pip install numpy
pip install scipy
pip install matplotlib
pip install sqlalchemy

# Copy config files from live environment
cp /etc/rn_irl/bin/rn_irl/.streamlit/*.toml /etc/rn_irl_staging/bin/rn_irl/.streamlit/
# Overwrite port config - staging should not run 443, let's use the default 8501 instead.
sed -i -e 's/port = 443/port = 8501/g' /etc/rn_irl_staging/bin/rn_irl/.streamlit/config.toml

# Change owner to rn_irl group
chown root:rn_irl -R /etc/rn_irl_staging

# Change ubuntu helpers.
cd /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers
sed -i -e 's/Really Nice IRL/Really Nice IRL STAGING/g' rn_irl.service
sed -i -e 's#/bin/rn_irl#/bin/rn_irl_staging.sh#g' rn_irl.service
sed -i -e 's#/etc/rn_irl/bin#/etc/rn_irl_staging/bin#g' rn_irl.sh
mv rn_irl.service rn_irl_staging.service
mv rn_irl.sh rn_irl_staging.sh
chmod +x rn_irl_staging.sh

# Create symlink
ln -sf /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging.sh /bin/rn_irl_staging
# Copy service
cp /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging.service /lib/systemd/system

# Reload, enable and run service.
systemctl daemon-reload
systemctl enable rn_irl_staging
service rn_irl_staging start
