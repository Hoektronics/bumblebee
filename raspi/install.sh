#!/bin/sh

sudo apt-get update -qy
sudo apt-get upgrade -qy

#install webcam tools
sudo apt-get install fswebcam uvcdynctrl v4l-utils python-picamera

#get Botqueue linked up and working on boot.
sudo apt-get install -qy git-core vim screen python-pip
sudo usermod -a -G dialout pi
sudo pip install pyserial Pygments requests requests-oauth

#make botqueue start on boot 
sudo /bin/sh -c 'cat /home/pi/bumblebee/raspi/inittab >> /etc/inittab'
cat $HOME/bumblebee/raspi/profile >> $HOME/.profile

cd ..
git submodule update --init

#authorize our app now.
screen -dR botqueue python -m bumblebee
