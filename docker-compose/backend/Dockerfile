FROM python:3.8-alpine

WORKDIR /usr/local/src

COPY ./requirements.txt ./

RUN pip install \
        --requirement ./requirements.txt

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000" ]

COPY ./guess ./repository ./run.py ./
