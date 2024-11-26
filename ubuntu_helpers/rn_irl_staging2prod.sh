#!/bin/bash

# Shut down staging service.
service rn_irl_staging stop

# Change all paths in the staging environment to the production environment path.
cd /etc/rn_irl_staging/
sed -i -e 's/rn_irl_staging/rn_irl/g' pyvenv.cfg

cd /etc/rn_irl_staging/bin

for entry in *

do
  if [ -f "$entry" ];then
    sed -i -e 's/rn_irl_staging/rn_irl/g' "$entry"
  fi
done

# Overwrite port config - move back to port 443.
sed -i -e 's/port = 8501/port = 443/g' /etc/rn_irl_staging/bin/rn_irl/.streamlit/config.toml

# Shut down production enviorment.
service rn_irl stop

# Back up current production environment.
DATE=$(date -I)
mv /etc/rn_irl /etc/rn_irl_$DATE

# Move staging enviroment path to production.
mv /etc/rn_irl_staging /etc/rn_irl
cp /etc/rn_irl/bin/ubuntu_helpers/rn_irl.sh /etc/rn_ril/bin/rn_irl.sh

# Restart production environment.
service rn_irl start

# Remove staging symlink.
rm /bin/rn_irl_staging
