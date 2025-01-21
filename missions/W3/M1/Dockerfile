FROM openjdk:8

# 작업 디렉토리 설정
WORKDIR /hadoop

# 필수 패키지 설치
RUN apt-get update && apt-get install -y wget tar ssh rsync sudo && \
    apt-get clean

COPY ./src/hadoop-3.4.1.tar.gz .

RUN tar -xzf hadoop-3.4.1.tar.gz && \
    mv hadoop-3.4.1 /usr/local/hadoop && \
    rm hadoop-3.4.1.tar.gz

ENV HADOOP_HOME=/usr/local/hadoop \
    HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop \
    PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin \
    HDFS_NAMENODE_USER=root \
    HDFS_DATANODE_USER=root \
    HDFS_SECONDARYNAMENODE_USER=root \
    YARN_RESOURCEMANAGER_USER=root \
    YARN_NODEMANAGER_USER=root

# SSH 설정 (Hadoop의 통신 필요)
RUN ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 600 ~/.ssh/authorized_keys

# Hadoop 구성 파일 복사
COPY conf/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY conf/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY conf/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml

# Java 실행 환경변수 hadoop에 설정.
RUN echo "export JAVA_HOME=$JAVA_HOME" >> /usr/local/hadoop/etc/hadoop/hadoop-env.sh

# 포트 오픈 (NameNode, DataNode, ResourceManager 등)
EXPOSE 9870 8088 9000 9864 22

COPY src/init.sh .
RUN chmod +x init.sh

ENTRYPOINT ["./init.sh"]