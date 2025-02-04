FROM openjdk:11

WORKDIR /spark

ARG spark_uid=185
RUN useradd --uid=${spark_uid} spark

RUN apt update && apt install -y python3 python3-pip
RUN apt-get update && apt-get install -y supervisor
RUN pip install ipykernel pyspark
RUN mkdir -p /opt/spark;\
    mkdir /opt/spark/python;\
    mkdir -p /opt/spark/examples;\
    mkdir -p /opt/spark/work-dir;\
    chmod g+w /opt/spark/work-dir;\
    touch /opt/spark/RELEASE;\
    chown -R spark:spark /opt/spark;\
    mkdir -p /tmp/spark-events;\
    chown -R spark:spark /tmp/spark-events

RUN mkdir -p /home/spark &&\
    chown -R spark:spark /home/spark

COPY src/spark-3.5.4-bin-hadoop3.tgz ./spark.tgz
RUN tar -xf spark.tgz --strip-components=1 &&\
    chown -R spark:spark . &&\
    rm -rf spark.tgz &&\
    mv * /opt/spark/

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV SPARK_NO_DAEMONIZE=1

WORKDIR /opt/spark/work-dir
COPY src/supervisord.conf .
COPY M2/nyc_taxi_analysis.py .
