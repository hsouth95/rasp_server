#! /bin/bash

echo "Running installer"
sudo echo "FLASK_APP=rasp_server" >> /etc/environment
sudo pip install flask --upgrade
sudo flask run -h 0.0.0.0
echo "Finished installing"