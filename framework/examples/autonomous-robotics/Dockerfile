# Smart402 Autonomous Robotics Platform - Docker Image
# Multi-stage build for optimized production image

# Stage 1: Build
FROM node:20-alpine AS builder

LABEL maintainer="Smart402 Team <team@smart402.io>"
LABEL description="Smart402 Autonomous Robotics Platform with Blockchain"

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++ git

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application source
COPY src/ ./src/
COPY contracts/ ./contracts/

# Stage 2: Production
FROM node:20-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    tini

# Create non-root user
RUN addgroup -g 1001 -S smart402 && \
    adduser -S -D -H -u 1001 -h /app -s /sbin/nologin -G smart402 -g smart402 smart402

# Copy from builder
COPY --from=builder --chown=smart402:smart402 /app/node_modules ./node_modules
COPY --from=builder --chown=smart402:smart402 /app/src ./src
COPY --from=builder --chown=smart402:smart402 /app/contracts ./contracts
COPY --chown=smart402:smart402 package*.json ./

# Create logs directory
RUN mkdir -p logs && chown -R smart402:smart402 logs

# Switch to non-root user
USER smart402

# Expose ports
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Use tini for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start application
CMD ["node", "src/index.js", "server"]
