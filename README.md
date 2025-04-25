# This is our implementation of KTHs brilliant Innovation Readiness Level framework.

The intention is to have a web tool that is both easily accessible and easy to use in meetings and workshops to assess and agreee where your project currently sits on the various IRL levels.
It is also possible to use it as a light weight project managament tool, as you can define targets and action points for each IRL level.

You can define project teams and access across organisations, faculties and departments as you see fit.

We recommend that you deploy this on an internal server.
A tutorial on how to do this with a custom domain in Apache2 can be found here:
https://q-viper.github.io/2022/07/17/deploying-streamlit-app-with-custom-domain-in-apache2/

I've made a quick guide and some helpers for getting this up and running on Linux server below. 
Note that this is only tested on Ubuntu 24.04 LTS, so if you're running something else YMMW.

# RN IRL Setup Guide

## Make sure Ubuntu is up to date.
sudo apt update  
sudo apt upgrade  

## Install some basics.
sudo apt install sqlite3  
sudo apt install python3-venv  
sudo apt install python-is-python3 


## Create a group for users that need access to rn_irl folders without root access (this is optional, but probably good practice if you want to restrict root access):
sudo groupadd --gid 99 rn_irl

## Get the source code - doesn't matter where you place it at this time.
git clone https://github.com/NTNU-TTO/rn_irl  
sudo chown root:rn_irl -R rn_irl  

## Set up a persistent python environment to run in.
cd /etc  
sudo python -m venv rn_irl  
sudo chown root:rn_irl -R rn_irl  

## Activate the virtual python environment.
source /etc/rn_irl/bin/activate  

## Install required python modules.
pip install streamlit  
pip install bcrypt  
pip install numpy  
pip install scipy  
pip install matplotlib  
pip install sqlalchemy  

## Move the source code inside the virtual python environment.
sudo mv /path/to/your/local/github/clone/rn_irl /etc/rn_irl/bin  

## Make the database persistent outside of the rn_irl environment
sudo mkdir /var/lib/rn_irl  
sudo mv /etc/rn_irl/bin/rn_irl/irl.sdb /var/lib/rn_irl  

## Edit secrets.toml and update the path to the database:
[db_details]  
db_path = 'sqlite:////var//lib//rn_irl//irl.sdb  

## Create symlink bash script:
sudo ln -s /etc/rn_irl/bin/rn_irl/ubuntu_helpers/rn_irl.sh /bin/rn_irl  

## Copy service
sudo cp /etc/rn_irl/bin/rn_irl/ubuntu_helpers/rn_irl.service /lib/systemd/system/  

## Reload, enable and run service
sudo systemctl daemon-reload  
sudo systemctl enable rn_irl  
sudo service rn_irl start  

## Enjoy.

You are free to implement any changes you like to the source code to tailor it to your own and/or your organisations need.
The source code is provided as is with absolutely no guarantees that it is useful or fit for purpose.

