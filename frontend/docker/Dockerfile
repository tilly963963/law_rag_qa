FROM python:3.9

COPY requirements.txt /

RUN pip3 install --upgrade pip &&  pip3 install --no-cache-dir -r /requirements.txt && rm /requirements.txt

ENV USER=nlpcat

RUN useradd -s /bin/bash -m $USER

CMD ["streamlit", "run", "app.py"]

COPY --chown=$USER:$USER . /app

USER $USER

WORKDIR /app
