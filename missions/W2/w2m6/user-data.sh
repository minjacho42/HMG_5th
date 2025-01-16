#!/bin/bash
yum update -y

##### SETUP SWAP MEMORY #####
# Create a 2GB swap file
SWAPFILE="/swapfile"
dd if=/dev/zero of=$SWAPFILE bs=1M count=2048
chmod 600 $SWAPFILE
mkswap $SWAPFILE
swapon $SWAPFILE
if ! grep -q "$SWAPFILE" /etc/fstab; then
  echo "$SWAPFILE swap swap defaults 0 0" >> /etc/fstab
fi
# Confirm swap status
swapon --show
#################################

##### INSTALL DOCKER, PULL & RUN IMAGE #####
sudo yum install -y docker
sudo service docker start

sudo usermod -a -G docker ec2-user

sudo docker pull public.ecr.aws/l1j1o8n7/hmg-5th/w2:latest
sudo docker run -d -p 9919:8888 -e NOTEBOOK_PWD=19990109 public.ecr.aws/l1j1o8n7/hmg-5th/w2:latest
############################################