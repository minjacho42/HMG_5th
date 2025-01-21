FROM openjdk:8

# 작업 디렉토리 설정
WORKDIR /hadoop

# 필수 패키지 설치
RUN apt-get update && apt-get install -y wget tar ssh rsync sudo && \
    apt-get clean

arg HADOOP_USER_PWD

# hadoop 사용자 생성 및 디렉토리 설정 (passwd가 명시됨. 보안상 이슈 발생 가능. 수정 필요)
RUN useradd -m -s /bin/bash hadoop && \
    echo "hadoop:${HADOOP_USER_PWD}" | chpasswd && \
    mkdir -p /home/hadoop/.ssh && \
    chown -R hadoop:hadoop /home/hadoop

# Hadoop 설치
COPY ./src/hadoop-3.4.1.tar.gz .
RUN tar -xzf hadoop-3.4.1.tar.gz && \
    mv hadoop-3.4.1 /usr/local/hadoop && \
    rm hadoop-3.4.1.tar.gz && \
    chown -R hadoop:hadoop /usr/local/hadoop

# 환경 변수 설정
ENV HADOOP_HOME=/usr/local/hadoop \
    HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop \
    PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin \
    HDFS_NAMENODE_USER=hadoop \
    HDFS_DATANODE_USER=hadoop \
    HDFS_SECONDARYNAMENODE_USER=hadoop \
    YARN_RESOURCEMANAGER_USER=hadoop \
    YARN_NODEMANAGER_USER=hadoop
#    JAVA_HOME=/usr/local/openjdk-8 설정하지 않아도 자동 설정됨.

# SSH 설정
RUN ssh-keygen -q -t rsa -N '' -f /home/hadoop/.ssh/id_rsa && \
    cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys && \
    chmod 600 /home/hadoop/.ssh/authorized_keys && \
    chown -R hadoop:hadoop /home/hadoop/.ssh && \
    chown -R hadoop:hadoop $JAVA_HOME

# Hadoop 구성 파일 복사
COPY conf/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY conf/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY conf/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml

# Java 실행 환경 변수 설정
RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# 초기화 스크립트 복사 및 실행 권한 설정
COPY src/init.sh /home/hadoop/init.sh
RUN chmod +x /home/hadoop/init.sh && chown hadoop:hadoop /home/hadoop/init.sh

# 데이터 디렉토리 권한 설정
RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data &&\
    chown -R hadoop:hadoop /hadoop/dfs/name /hadoop/dfs/data

# 포트 오픈 (NameNode, DataNode, ResourceManager 등)
EXPOSE 9870 8088 9000 9864 22

ENTRYPOINT ["/home/hadoop/init.sh"]