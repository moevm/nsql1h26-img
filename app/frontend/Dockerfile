FROM node:22-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts

FROM base AS dev
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM base AS builder
COPY . .
RUN npm run build

FROM nginx:1.30.0-alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
