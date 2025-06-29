FROM python:3.8-alpine

LABEL org.opencontainers.image.title="guess_game_backend" \
      org.opencontainers.image.description="Guess Game Backend" \
      org.opencontainers.image.authors="Wanderson Camargo <wandersonwhcr@gmail.com>"

RUN pip install pyuwsgi \
        --no-cache-dir

ENTRYPOINT [ "uwsgi" ]

CMD [ "--http=0.0.0.0:5000", "--master", "--processes=4", "--module", "guess:create_app()" ]

EXPOSE 5000

WORKDIR /usr/local/src

COPY ./requirements.txt ./

RUN pip install \
        --no-cache-dir \
        --requirement ./requirements.txt

# Impossível Utilizar ./guess ./repository ./run.py ./
COPY guess ./guess
COPY repository ./repository
COPY run.py ./run.py
