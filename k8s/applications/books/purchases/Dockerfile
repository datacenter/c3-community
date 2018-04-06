FROM node:argon
WORKDIR /purchases
COPY purchases.js swagger.json package.json /purchases/
RUN npm install
ENTRYPOINT ["node", "purchases.js", "--memory"]
