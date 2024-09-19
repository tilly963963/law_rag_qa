FROM python:3.9

COPY requirements.txt /

RUN pip3 install --upgrade pip &&  pip3 install --no-cache-dir -r /requirements.txt && rm /requirements.txt

ENV USER=nlpcat

RUN echo create user $USER
RUN useradd -s /bin/bash -m $USER

CMD ["/app/entrypoint.sh"]
# CMD ["/bin/bash"]
# ENTRYPOINT ["/bin/bash"]

COPY --chown=$USER:$USER . /app

USER $USER

WORKDIR /app
