FROM node:18.17-alpine

LABEL org.opencontainers.image.title="guess_game_frontend" \
      org.opencontainers.image.description="Guess Game Frontend" \
      org.opencontainers.image.authors="Wanderson Camargo <wandersonwhcr@gmail.com>"

EXPOSE 3000

ENTRYPOINT [ "yarn" ]

CMD [ "start" ]

WORKDIR /usr/local/src

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install \
        --production

COPY ./frontend ./
