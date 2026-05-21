FROM node:20-alpine AS build

ARG VITE_API_URL=http://127.0.0.1:8100
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

COPY package.json ./
RUN npm install

COPY index.html vite.config.ts tsconfig.json ./
COPY src ./src

RUN npm run build

FROM node:20-alpine

WORKDIR /app

RUN npm install -g serve@14

COPY --from=build /app/dist ./dist

EXPOSE 5174

CMD ["serve", "-s", "dist", "-l", "5174"]
