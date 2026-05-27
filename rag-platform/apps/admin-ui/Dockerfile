FROM node:20-alpine

ARG VITE_API_URL=http://127.0.0.1:8100
ARG HTTP_PROXY=
ARG HTTPS_PROXY=
ARG NO_PROXY=

ENV VITE_API_URL=$VITE_API_URL \
    NPM_CONFIG_FETCH_RETRIES=5 \
    NPM_CONFIG_FETCH_TIMEOUT=300000 \
    HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    NO_PROXY=$NO_PROXY \
    http_proxy=$HTTP_PROXY \
    https_proxy=$HTTPS_PROXY \
    no_proxy=$NO_PROXY

WORKDIR /app

# npm install/build runs at container start (entrypoint) so corporate DNS and proxy apply on Windows.
COPY package.json package-lock.json* docker-entrypoint.sh ./
COPY index.html vite.config.ts tsconfig.json ./
COPY src ./src

RUN chmod +x docker-entrypoint.sh

EXPOSE 5174

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5174"]
