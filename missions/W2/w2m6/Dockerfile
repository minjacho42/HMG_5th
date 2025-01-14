FROM python:slim

RUN apt-get update && apt-get install -y gcc

RUN pip install --upgrade pip

# Python 패키지 설치
RUN pip install pandas matplotlib wordcloud numpy jupyter notebook

RUN mkdir src

RUN jupyter notebook --generate-config

COPY ./config/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

COPY ./src src

EXPOSE 8888

ENTRYPOINT ["jupyter", "lab", "--allow-root", "--ip", "0.0.0.0"]