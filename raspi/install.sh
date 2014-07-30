#!/bin/sh

sudo apt-get update -qy
sudo apt-get upgrade -qy

#install webcam tools
sudo apt-get install fswebcam uvcdynctrl v4l-utils

#get Botqueue linked up and working on boot.
sudo apt-get install -qy git-core vim screen python-pip
git clone https://github.com/Hoektronics/bumblebee.git
sudo usermod -a -G dialout pi
sudo pip install pyserial Pygments requests requests-oauth

#make botqueue start on boot 
sudo /bin/sh -c 'cat /home/pi/BotQueue/bumblebee/raspi/inittab >> /etc/inittab'
chmod a+x $HOME/BotQueue/bumblebee/raspi/bin/bumblebee
cat $HOME/BotQueue/bumblebee/raspi/profile >> $HOME/.profile
source $HOME/.profile

#authorize our app now.
screen -dR botqueue bumblebee
