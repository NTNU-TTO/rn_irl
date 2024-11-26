#!/bin/bash

echo "Setting up virtual environment for python..."
# Sets up a staging environment for testing bleeding edge RN IRL straight outta github.
cd /etc
# Set up a virtual environment for python
python -m venv rn_irl_staging

# Clone latest'n'greatest to the staging environment.
echo "Getting bleeding edge from github..."
cd /etc/rn_irl_staging/bin
git clone https://github.com/NTNU-TTO/rn_irl
# Source and install requirements
echo "Installing requirements..."
source /etc/rn_irl_staging/bin/activate
cd /etc/rn_irl_staging
pip install streamlit
pip install bcrypt
pip install numpy
pip install scipy
pip install matplotlib
pip install sqlalchemy

# Copy config files from live environment
echo "Duplicating existing configuration..."
cp /etc/rn_irl/bin/rn_irl/.streamlit/*.toml /etc/rn_irl_staging/bin/rn_irl/.streamlit/
# Overwrite port config - staging should not run 443, let's use the default 8501 instead.
sed -i -e 's/port = 443/port = 8501/g' /etc/rn_irl_staging/bin/rn_irl/.streamlit/config.toml

# Change owner to rn_irl group
chown root:rn_irl -R /etc/rn_irl_staging

# Create symlink
chomd ug+x /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl.sh
chomd ug+x /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging_env.sh
chomd ug+x /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging2prod.sh
ln -sf /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging_env.sh /bin/rn_irl_staging

# Copy service
cp /etc/rn_irl_staging/bin/rn_irl/ubuntu_helpers/rn_irl_staging.service /lib/systemd/system

# Reload, enable and run service.
echo "Starting staging environment..."
systemctl daemon-reload
systemctl enable rn_irl_staging
service rn_irl_staging start
