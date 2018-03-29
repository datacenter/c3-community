FROM node:argon
WORKDIR /users
COPY users.js swagger.json package.json /users/
RUN npm install
ENTRYPOINT ["node", "users.js", "--memory"]
