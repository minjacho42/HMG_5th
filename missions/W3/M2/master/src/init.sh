#!/bin/bash

# SSH 서비스 시작 (root 권한으로 실행)
service ssh start

# hadoop 사용자로 전환
su - hadoop <<EOF

# NameNode 포맷 (최초 실행 시에만)
if [ ! -d "/hadoop/dfs/name" ] || [ -z "$(ls -A /hadoop/dfs/name)" ]; then
    echo "Formatting NameNode..."
    $HADOOP_HOME/bin/hdfs namenode -format -force
else
    echo "NameNode already formatted. Skipping format."
fi

# HDFS 서비스 시작
echo "Starting HDFS services..."
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

EOF

# 포그라운드 유지 및 로그 출력
tail -f $HADOOP_HOME/logs/*.log