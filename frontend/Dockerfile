FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

ARG API_PROXY_URL=http://backend:8000
ENV API_PROXY_URL=${API_PROXY_URL}

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
