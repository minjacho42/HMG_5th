#!/bin/bash

# SSH 서비스 시작 (root 권한으로 실행)
service ssh start

# hadoop 사용자로 전환
#su - hadoop <<EOF
#
## HDFS 서비스 시작
#echo "Starting HDFS services..."
#$HADOOP_HOME/bin/hdfs --daemon start datanode
#
#EOF

# 포그라운드 유지 및 로그 출력
tail -f /dev/null