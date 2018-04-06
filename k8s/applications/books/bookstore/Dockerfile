FROM node:argon
WORKDIR /bookstore
COPY bookstore.js swagger.json package.json /bookstore/
RUN npm install
ENTRYPOINT ["node", "bookstore.js", "--memory"]
