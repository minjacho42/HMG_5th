#!/bin/bash

service ssh start

# NameNode 포맷 (최초 실행 시에만)
if [ ! -d "/hadoop/dfs/name" ] || [ -z "$(ls -A /hadoop/dfs/name)" ]; then
    echo "Formatting NameNode..."
    $HADOOP_HOME/bin/hdfs namenode -format -force
else
    echo "NameNode already formatted. Skipping format."
fi

# HDFS 시작
$HADOOP_HOME/sbin/start-dfs.sh

# 포그라운드 유지 및 로그 출력
tail -f $HADOOP_HOME/logs/*.log