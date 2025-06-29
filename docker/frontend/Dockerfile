FROM node:18.17-alpine AS build

LABEL org.opencontainers.image.title="guess_game_frontend" \
      org.opencontainers.image.description="Guess Game Frontend" \
      org.opencontainers.image.authors="Wanderson Camargo <wandersonwhcr@gmail.com>"

ENTRYPOINT [ "yarn" ]

CMD [ "start" ]

EXPOSE 3000

WORKDIR /usr/local/src

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install

ENV REACT_APP_BACKEND_URL="http://localhost:5000"

COPY ./frontend ./

RUN npm run build

FROM nginx:1.29-alpine AS release

COPY ./docker/frontend/configs/nginx-template-default.conf /etc/nginx/templates/default.conf.template

COPY --from=build /usr/local/src/build /usr/share/nginx/html
