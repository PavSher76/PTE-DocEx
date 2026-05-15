FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --include=optional \
  && arch="$(uname -m)" \
  && case "$arch" in \
       x86_64) rollup_pkg="@rollup/rollup-linux-x64-musl@4.60.3" ;; \
       aarch64|arm64) rollup_pkg="@rollup/rollup-linux-arm64-musl@4.60.3" ;; \
       *) echo "unsupported arch: $arch" >&2; exit 1 ;; \
     esac \
  && npm install "$rollup_pkg" --no-save

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["npm", "run", "dev"]
