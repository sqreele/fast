# Base stage with Node.js and pnpm
FROM node:20-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    curl \
    libc6-compat \
    && corepack enable \
    && corepack prepare pnpm@latest --activate

WORKDIR /app

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED=1

# Dependencies stage
FROM base AS deps

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./

# Install all dependencies (including devDependencies) for building
RUN \
  if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci --include=dev; \
  elif [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Development stage
FROM base AS development

# Install curl for health checks and development tools
RUN apk add --no-cache curl git

# Create nextjs user with specific UID/GID for development
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy node_modules from deps stage
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules

# Copy application code
COPY --chown=nextjs:nodejs . .

# Create necessary directories with proper permissions
RUN mkdir -p .next .next/cache .next/server .next/static && \
    touch next-env.d.ts && \
    chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Development command with hot reloading
CMD ["npm", "run", "dev"]

# Builder stage for production
FROM base AS builder

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

# Set build-time environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Build the application
RUN \
  if [ -f yarn.lock ]; then yarn build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then pnpm build; \
  else npm run build; \
  fi

# Production stage - simplified
FROM base AS production

# Create nextjs user for production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 --ingroup nodejs nextjs

# Install curl for health checks
RUN apk add --no-cache curl

# Set production environment
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

WORKDIR /app

# Copy package.json and node_modules
COPY --from=deps --chown=nextjs:nodejs /app/package.json ./
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/next.config.* ./

USER nextjs

EXPOSE 3000

# Production health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Use npm start instead of standalone
CMD ["npm", "start"] 