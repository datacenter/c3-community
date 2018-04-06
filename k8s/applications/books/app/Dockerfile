FROM node:boron

WORKDIR /app
COPY package.json .
RUN npm install
COPY .angular-cli.json .
COPY src src
RUN npm run build
RUN rm -rf src

COPY app.js .

ENV PORT 8080
EXPOSE $PORT
ENTRYPOINT ["node", "app.js"]
