#!/bin/bash

echo -n "c.NotebookApp.password = u'" >> /root/.jupyter/jupyter_notebook_config.py && \
    python3 -c 'import os; from jupyter_server import auth; print(auth.passwd(os.environ["NOTEBOOK_PWD"]), end="")' >> /root/.jupyter/jupyter_notebook_config.py && \
    echo -n "'"  >> /root/.jupyter/jupyter_notebook_config.py

exec jupyter lab --allow-root --ip=0.0.0.0