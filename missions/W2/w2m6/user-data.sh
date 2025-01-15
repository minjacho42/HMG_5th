#!/bin/bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start

sudo usermod -a -G docker ec2-user

sudo docker pull public.ecr.aws/l1j1o8n7/hmg-5th/w2:latest
sudo docker run -d -p 9919:8888 -e NOTEBOOK_PWD=19990109 public.ecr.aws/l1j1o8n7/hmg-5th/w2:latest