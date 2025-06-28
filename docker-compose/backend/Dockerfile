FROM python:3.8-alpine

WORKDIR /usr/local/src

COPY ./requirements.txt ./

RUN pip install \
        --requirement ./requirements.txt

ENV FLASK_APP="run.py"
ENV FLASK_DB_TYPE=""
ENV FLASK_DB_USER=""
ENV FLASK_DB_NAME=""
ENV FLASK_DB_PASSWORD=""
ENV FLASK_DB_HOST=""
ENV FLASK_DB_PORT=""

EXPOSE 5000

ENTRYPOINT [ "flask" ]

CMD [ "run", "--host=0.0.0.0", "--port=5000" ]

COPY guess ./guess
COPY repository ./repository
COPY run.py ./run.py
