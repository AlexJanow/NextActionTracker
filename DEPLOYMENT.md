# Deployment Guide

This document provides detailed instructions for deploying the Next Action Tracker in different environments.

## Development Deployment

### Quick Start
```bash
# Clone and start
git clone <repository-url>
cd next-action-tracker
make up
make seed
```

### Manual Setup
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check health
make health

# Seed demo data
docker-compose exec backend python -m app.database.seed
```

## Production Deployment

### Prerequisites
- Docker and Docker Compose
- SSL certificates (for HTTPS)
- Domain name configured
- Environment variables configured

### Environment Setup

Create production environment file:
```bash
# .env.prod
DB_USER=nat_prod_user
DB_PASSWORD=<secure-password>
API_URL=https://api.yourdomain.com
TENANT_ID=<production-tenant-id>
```

### Production Commands
```bash
# Build production images
make prod-build

# Start production environment
DB_PASSWORD=<secure-password> make prod-up

# Check status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### SSL Configuration

For production with SSL, add a reverse proxy:

```yaml
# docker-compose.ssl.yml
services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - backend
```

## Cloud Deployment

### AWS ECS
1. Build and push images to ECR
2. Create ECS task definitions
3. Set up RDS PostgreSQL instance
4. Configure Application Load Balancer
5. Deploy services

### Google Cloud Run
1. Build images with Cloud Build
2. Deploy backend to Cloud Run
3. Deploy frontend to Cloud Run or Firebase Hosting
4. Use Cloud SQL for PostgreSQL
5. Configure IAM and networking

### Azure Container Instances
1. Push images to Azure Container Registry
2. Create container groups
3. Use Azure Database for PostgreSQL
4. Configure Application Gateway

## Monitoring and Logging

### Health Checks
All services include health check endpoints:
- Database: `pg_isready`
- Backend: `GET /health`
- Frontend: `GET /` (nginx)

### Logging Configuration
```yaml
# docker-compose.logging.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring Stack
Consider adding:
- Prometheus for metrics
- Grafana for dashboards
- Loki for log aggregation
- Jaeger for tracing

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U nat_user nat_dev > backup.sql

# Restore backup
docker-compose exec -T db psql -U nat_user nat_dev < backup.sql
```

### Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

## Security Considerations

### Production Security Checklist
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS encryption
- [ ] Implement proper authentication
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Use secrets management
- [ ] Enable audit logging

### Network Security
```yaml
# Restrict database access
services:
  db:
    ports: []  # Don't expose database port
    networks:
      - internal
```

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check port conflicts
netstat -tulpn | grep :3000
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose exec backend python -c "
from app.database.connection import get_database_url
print('Database URL:', get_database_url())
"
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec db psql -U nat_user -d nat_dev -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
"
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer for multiple frontend instances
- Scale backend with container orchestration
- Use read replicas for database scaling

### Vertical Scaling
- Increase container resource limits
- Optimize database configuration
- Use connection pooling

### Performance Optimization
- Enable database query caching
- Use CDN for static assets
- Implement Redis for session storage
- Add database indexes for common queries