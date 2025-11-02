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

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
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

# Create directories and set permissions
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run \
    && useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app/backend \
    && chown -R www-data:www-data /usr/share/nginx/html \
    && chown -R www-data:www-data /var/log/nginx \
    && chown -R www-data:www-data /etc/nginx \
    && chown -R root:root /var/log/supervisor

# Set Python path
ENV PYTHONPATH=/app/backend
ENV PATH="/usr/local/bin:${PATH}"

# Expose port 80 (nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start supervisor which manages both nginx and uvicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

