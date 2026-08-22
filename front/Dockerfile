FROM node:20-alpine AS build

WORKDIR /app

COPY front/package.json front/package-lock.json ./
RUN npm ci

COPY front/ ./
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location /api/ { proxy_pass https://back-production-820d.up.railway.app; proxy_set_header Host back-production-820d.up.railway.app; proxy_ssl_server_name on; }\n\
  location /health { proxy_pass https://back-production-820d.up.railway.app; proxy_set_header Host back-production-820d.up.railway.app; proxy_ssl_server_name on; }\n\
  location / { try_files $uri $uri/ /index.html; }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
