FROM python:slim

RUN apt-get update && apt-get install -y gcc

RUN pip install --upgrade pip
RUN pip install pandas matplotlib \
    wordcloud numpy jupyter \
    notebook kagglehub

RUN mkdir src

RUN jupyter notebook --generate-config

COPY ./config/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py
COPY ./src src
COPY ./config/entry.sh /entry.sh
RUN chmod +x /entry.sh

EXPOSE 8888

ENTRYPOINT ["/entry.sh"]