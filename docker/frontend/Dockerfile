FROM node:18.17-alpine

EXPOSE 3000

ENTRYPOINT [ "yarn" ]

CMD [ "start" ]

WORKDIR /usr/local/src

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install \
        --production

COPY ./frontend ./
