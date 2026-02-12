FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json ./package.json
COPY tsconfig.json ./tsconfig.json
COPY next.config.ts ./next.config.ts
COPY postcss.config.mjs ./postcss.config.mjs
COPY tailwind.config.ts ./tailwind.config.ts
COPY next-env.d.ts ./next-env.d.ts
COPY app ./app
COPY components ./components
COPY lib ./lib
COPY public ./public

RUN npm install
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000
CMD ["sh", "-c", "npm run start -- -p ${PORT:-3000}"]
