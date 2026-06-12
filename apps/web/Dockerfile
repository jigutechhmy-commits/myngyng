FROM node:20-slim

WORKDIR /workspace

COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/shared/package.json ./packages/shared/package.json
RUN npm ci

COPY packages/shared ./packages/shared
COPY apps/web ./apps/web

WORKDIR /workspace/apps/web
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
