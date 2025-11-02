# Multi-stage build for production deployment on Render
# Combines Frontend (React) and Backend (FastAPI) in a single container

# Stage 1: Frontend Build
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files (include package-lock.json for reproducible builds)
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
# Build with production environment variables
ARG REACT_APP_API_URL=/api/v1
ARG REACT_APP_TENANT_ID
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_TENANT_ID=${REACT_APP_TENANT_ID}

RUN npm run build

# Stage 2: Backend Setup
FROM python:3.11-slim AS backend-setup

WORKDIR /app/backend

# Install system dependencies (curl not needed here, but included for consistency)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies including PostgreSQL
# First, add PostgreSQL official APT repository for PostgreSQL 15
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Add PostgreSQL GPG key and repository
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Install PostgreSQL 15 and other dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    postgresql-15 \
    postgresql-contrib-15 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from backend-setup
COPY --from=backend-setup /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-setup /usr/local/bin /usr/local/bin

# Copy built frontend from frontend-builder
COPY --from=frontend-builder /app/frontend/build /usr/share/nginx/html

# Copy backend application code
COPY backend/ /app/backend/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy database init script and startup script
COPY database/init.sql /docker-entrypoint-initdb.d/init.sql
COPY start_postgres.sh /usr/local/bin/start_postgres.sh
RUN chmod +x /usr/local/bin/start_postgres.sh

# Create directories and set permissions
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run /var/lib/postgresql/data /root/.postgresql \
    && useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app/backend \
    && chown -R www-data:www-data /usr/share/nginx/html \
    && chown -R www-data:www-data /var/log/nginx \
    && chown -R www-data:www-data /etc/nginx \
    && chown -R root:root /var/log/supervisor \
    && chown -R postgres:postgres /var/lib/postgresql/data \
    && chmod 700 /var/lib/postgresql/data \
    && chmod 755 /root/.postgresql

# Set Python path
ENV PYTHONPATH=/app/backend
ENV PATH="/usr/local/bin:${PATH}"

# PostgreSQL environment variables
ENV POSTGRES_USER=nat_user
ENV POSTGRES_PASSWORD=nat_password
ENV POSTGRES_DB=nat_dev
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Default DATABASE_URL (can be overridden)
ENV DATABASE_URL=postgresql://nat_user:nat_password@localhost:5432/nat_dev

# Note: PostgreSQL will be initialized at runtime by start_postgres.sh

# Expose port 80 (nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start supervisor which manages both nginx and uvicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

