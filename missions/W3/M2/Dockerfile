FROM openjdk:8

# 작업 디렉토리 설정
WORKDIR /hadoop

# 필수 패키지 설치
RUN apt-get update && apt-get install -y wget tar ssh rsync sudo && \
    apt-get clean

ARG HADOOP_USER_PWD

# 루트 권한으로 작업 수행
RUN mkdir -p /root/.ssh && \
    mkdir -p /hadoop && \
    mkdir -p /tmp/logs

RUN chown -R root:root /tmp/logs &&\
    chmod -R 755 /tmp/logs

# Hadoop 설치
COPY ./src/hadoop-3.4.1.tar.gz .
RUN tar -xzf hadoop-3.4.1.tar.gz && \
    mv hadoop-3.4.1 /usr/local/hadoop && \
    rm hadoop-3.4.1.tar.gz

# 환경 변수 설정
ENV HADOOP_HOME=/usr/local/hadoop \
    HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop \
    PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin \
    HDFS_NAMENODE_USER=root \
    HDFS_DATANODE_USER=root \
    HDFS_SECONDARYNAMENODE_USER=root \
    YARN_RESOURCEMANAGER_USER=root \
    YARN_NODEMANAGER_USER=root

# SSH 설정
RUN ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

# Hadoop 구성 파일 복사
COPY ./conf/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY ./conf/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY ./conf/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
COPY ./conf/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
COPY ./conf/workers $HADOOP_HOME/etc/hadoop/workers

# Java 실행 환경 변수 설정
RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo "export HADOOP_DATANODE_HOSTNAME=$HADOOP_DATANODE_HOSTNAME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo "export HADOOP_OPTS=\"$HADOOP_OPTS -DHADOOP_DATANODE_HOSTNAME=$HADOOP_DATANODE_HOSTNAME\"" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# 초기화 스크립트 복사 및 실행 권한 설정
COPY src/init.sh /root/init.sh
RUN chmod +x /root/init.sh

# 데이터 디렉토리 권한 설정
RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data

# 포트 오픈 (NameNode, DataNode, ResourceManager 등)
EXPOSE 9870 8088

ENTRYPOINT ["/root/init.sh"]