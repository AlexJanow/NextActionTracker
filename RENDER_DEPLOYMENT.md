# Render Deployment Guide

This project is configured to deploy both Frontend (React) and Backend (FastAPI) in a single Docker container on Render.

## Architecture

- **Frontend**: React SPA built and served as static files via nginx
- **Backend**: FastAPI running on uvicorn (port 8000, internal)
- **Reverse Proxy**: nginx proxies `/api/*` requests to the backend
- **Process Manager**: supervisord manages both nginx and uvicorn processes

## Deployment Steps

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Render will automatically detect the `Dockerfile` in the root

2. **Environment Variables**

   Set these in Render's environment variables:

   **Backend:**
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ENVIRONMENT=production
   PYTHONPATH=/app/backend
   ALLOWED_ORIGINS=https://your-app-name.onrender.com
   ```

   **Frontend (build-time):**
   ```
   REACT_APP_API_URL=/api/v1
   REACT_APP_TENANT_ID=your-tenant-id
   ```

3. **PostgreSQL Database**

   - Create a PostgreSQL database service on Render
   - Copy the internal database URL
   - Set it as `DATABASE_URL` environment variable

4. **Build Settings**

   Render should automatically:
   - Detect the Dockerfile
   - Build the multi-stage Docker image
   - Deploy to a web service

5. **Health Checks**

   The service includes a health check endpoint at `/health` that checks the backend API.

## Service Structure

```
Container Port 80 (exposed)
  └── nginx (frontend static files + API proxy)
       ├── / → React SPA
       └── /api/* → proxy to localhost:8000
            └── uvicorn (FastAPI backend)
```

## Troubleshooting

- **Check logs**: Render dashboard → Logs tab
- **Backend logs**: Managed by supervisord, available in container at `/var/log/supervisor/backend.log`
- **nginx logs**: Available at `/var/log/supervisor/nginx.log`
- **Health check fails**: Verify `DATABASE_URL` is set correctly and database is accessible

## Local Testing

To test the Docker build locally:

```bash
docker build -t next-action-tracker .
docker run -p 8080:80 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REACT_APP_API_URL=/api/v1 \
  -e REACT_APP_TENANT_ID=your-tenant-id \
  next-action-tracker
```

Then visit `http://localhost:8080`

