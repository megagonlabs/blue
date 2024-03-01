FROM node:18-alpine
WORKDIR /src
RUN npm config set "@fortawesome:registry" https://npm.fontawesome.com/
ARG fa_token
RUN npm config set "//npm.fontawesome.com/:_authToken" ${fa_token}
ENV PORT 3000
COPY ./src /src
RUN npm install
RUN npm run build
CMD ["npm", "run", "start"]