FROM node:22-alpine

ARG HTTP_PROXY=
ARG HTTPS_PROXY=
ARG NO_PROXY=

ENV NPM_CONFIG_FETCH_RETRIES=5 \
    NPM_CONFIG_FETCH_TIMEOUT=300000 \
    HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    NO_PROXY=$NO_PROXY \
    http_proxy=$HTTP_PROXY \
    https_proxy=$HTTPS_PROXY \
    no_proxy=$NO_PROXY

WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -n "$HTTP_PROXY" ]; then \
      npm config set proxy "$HTTP_PROXY"; \
      npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"; \
    fi \
    && npm ci --include=optional

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["npm", "run", "dev"]
