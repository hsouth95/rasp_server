#! /bin/bash

echo "Running installer"
sudo pip install -e .
sudo pip install flask --upgrade
echo "Creating Home...."
echo -n "Enter the name of your home and press [ENTER]: "
read name
sudo echo "FLASK_APP=rasp_server" >> /etc/environment
sudo export FLASK_APP=rasp_server
sudo flask initdb
sqlite3 ras_server/rasp_server.db "insert into home (name) values($name)"
sudo flask run -h 0.0.0.0
echo "Finished installing"