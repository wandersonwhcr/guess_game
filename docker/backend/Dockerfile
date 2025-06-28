FROM python:3.8-alpine

LABEL org.opencontainers.image.title="guess_game_backend" \
      org.opencontainers.image.description="Guess Game Backend" \
      org.opencontainers.image.authors="Wanderson Camargo <wandersonwhcr@gmail.com>"

EXPOSE 5000

ENV FLASK_APP="run.py"

ENTRYPOINT [ "flask" ]

CMD [ "run", "--host=0.0.0.0", "--port=5000" ]

WORKDIR /usr/local/src

COPY ./requirements.txt ./

RUN pip install \
        --requirement ./requirements.txt

# Impossível Utilizar ./guess ./repository ./run.py ./
COPY guess ./guess
COPY repository ./repository
COPY run.py ./run.py
