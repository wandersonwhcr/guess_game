FROM node:18.17-alpine

WORKDIR /usr/local/src

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install \
        --production

ENV REACT_APP_BACKEND_URL=""

EXPOSE 3000

ENTRYPOINT [ "yarn" ]

CMD [ "start" ]

COPY ./frontend ./
