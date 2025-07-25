# Project Management System - Docker Setup

A modern, production-ready Docker setup for a full-stack Project Management System built with FastAPI, Next.js, PostgreSQL, and Nginx.

## 🚀 Features

### Infrastructure
- **Multi-stage Docker builds** for optimized production images
- **Development and production environments** with separate configurations
- **Custom networking** with isolated subnets
- **Advanced health checks** and monitoring
- **Automatic SSL certificate generation**
- **Comprehensive logging** and log rotation

### Security
- **Non-root containers** with proper user management
- **Security headers** and OWASP compliance
- **Rate limiting** and DDoS protection
- **Read-only containers** where possible
- **Resource limits** and quotas
- **Network isolation** and security groups

### Performance
- **Nginx caching** with multiple cache zones
- **Database optimization** with tuned PostgreSQL settings
- **Static asset optimization** with aggressive caching
- **Connection pooling** and keep-alive
- **Gzip compression** and content optimization
- **Load balancing** with upstream health checks

### Monitoring & Backup
- **Prometheus metrics** collection
- **Grafana dashboards** for visualization
- **Automated database backups** with retention policies
- **Redis caching** for session management
- **Log aggregation** and rotation

## 📋 Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Make (for using Makefile commands)
- 4GB+ RAM for production setup
- 2GB+ free disk space

## 🛠️ Quick Start

### Development Environment

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd <your-project>
   make setup  # Copies .env.example to .env
   ```

2. **Edit environment variables**:
   ```bash
   nano .env  # Configure your settings
   ```

3. **Start development environment**:
   ```bash
   make dev  # or make quick-start
   ```

4. **Access services**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Adminer: http://localhost:8081
   - PgAdmin: http://localhost:5050

### Production Environment

1. **Setup production environment**:
   ```bash
   make quick-prod  # Generates SSL certs and starts production
   ```

2. **Or step by step**:
   ```bash
   make ssl-cert    # Generate SSL certificates
   make prod-build  # Build and start production
   ```

3. **Access monitoring**:
   ```bash
   make monitoring  # Start Prometheus + Grafana
   ```
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (admin/admin)

## 📖 Available Commands

View all available commands:
```bash
make help
```

### Development Commands
```bash
make dev          # Start development environment
make dev-build    # Build and start development
make dev-logs     # Show development logs
make dev-down     # Stop development environment
make dev-clean    # Clean development environment
```

### Production Commands
```bash
make prod         # Start production environment
make prod-build   # Build and start production
make prod-logs    # Show production logs
make prod-down    # Stop production environment
```

### Database Commands
```bash
make db-shell     # Access PostgreSQL shell
make db-backup    # Create database backup
make db-restore BACKUP=file.sql  # Restore from backup
```

### Development Tools
```bash
make shell-api       # Access FastAPI container
make shell-frontend  # Access Next.js container
make test           # Run backend tests
make lint           # Run code linting
make format         # Format code
```

### Monitoring & Maintenance
```bash
make monitoring     # Start monitoring stack
make health        # Check service health
make clean         # Clean Docker resources
make update        # Update all containers
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Database
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://pm_user:password@pm_postgres_db:5432/pm_database

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
NEXTAUTH_SECRET=your-nextauth-secret-min-32-chars

# Production
ENVIRONMENT=production
WORKERS=4
LOG_LEVEL=WARNING

# Monitoring
GRAFANA_ADMIN_PASSWORD=secure-admin-password
```

### Development vs Production

The setup automatically detects environment and applies appropriate configurations:

**Development Features:**
- Hot reloading for frontend and backend
- Debug logging and detailed error messages
- Development tools (PgAdmin, Mailhog, File Browser)
- Direct port exposure for services
- Volume mounts for live code editing

**Production Features:**
- Optimized container images
- Enhanced security headers
- Automated backups
- Monitoring and alerting
- Resource limits and scaling
- SSL/TLS encryption

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │◄───┤   Next.js       │    │    FastAPI      │
│   (Reverse      │    │  (Frontend)     │    │   (Backend)     │
│    Proxy)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Prometheus    │
│   (Database)    │    │   (Cache)       │    │  (Monitoring)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Services

- **Nginx**: Reverse proxy, load balancer, SSL termination
- **Next.js**: React frontend with SSR/SSG
- **FastAPI**: Python backend API
- **PostgreSQL**: Primary database with optimized settings
- **Redis**: Caching and session storage
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Adminer**: Database administration

## 🔍 Monitoring

### Health Checks

All services include comprehensive health checks:
- HTTP endpoint monitoring
- Database connectivity checks
- Resource utilization monitoring
- Custom application metrics

### Logging

Centralized logging with:
- Structured JSON logs
- Log rotation and retention
- Different log levels per environment
- Request/response logging

### Metrics

Prometheus metrics include:
- Application performance metrics
- Database performance
- HTTP request metrics
- System resource usage
- Custom business metrics

## 🔒 Security Features

### Container Security
- Non-root user execution
- Read-only root filesystems
- Minimal base images (Alpine Linux)
- Security scanning integration
- Capability dropping

### Network Security
- Isolated Docker networks
- Internal service communication
- Rate limiting and DDoS protection
- Security headers (HSTS, CSP, etc.)

### Data Protection
- Encrypted database connections
- SSL/TLS for all external traffic
- Secure credential management
- Regular security updates

## 🚀 Performance Optimizations

### Caching Strategy
- Multi-level caching (Nginx, Redis, Browser)
- Static asset optimization
- Database query caching
- API response caching

### Database Tuning
- Optimized PostgreSQL configuration
- Connection pooling
- Query optimization
- Regular maintenance tasks

### Frontend Optimization
- Next.js optimization features
- Static generation where possible
- Image optimization
- Bundle splitting

## 🔄 Backup & Recovery

### Automated Backups
- Daily PostgreSQL dumps
- Configurable retention policies
- Compressed backup storage
- Health monitoring of backup process

### Disaster Recovery
```bash
# Create backup
make db-backup

# Restore from backup
make db-restore BACKUP=backup_20240101_120000.sql

# Full system backup (manual)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  run --rm postgres_backup /backup.sh
```

## 🐛 Troubleshooting

### Common Issues

**Services not starting:**
```bash
make health  # Check service status
make logs    # Check logs for errors
```

**Database connection issues:**
```bash
make db-shell  # Test database connectivity
make logs-db   # Check database logs
```

**Permission issues:**
```bash
make dev-clean  # Clean and restart
sudo chown -R $USER:$USER .  # Fix file permissions
```

**Performance issues:**
```bash
make monitoring  # Check Grafana dashboards
docker stats     # Check resource usage
```

### Debug Mode

Enable debug mode for troubleshooting:
```bash
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG

# Restart services
make restart
```

## 📚 Development Workflow

1. **Start development environment**:
   ```bash
   make dev
   ```

2. **Make code changes** (auto-reload enabled)

3. **Run tests**:
   ```bash
   make test
   make test-frontend
   ```

4. **Code quality checks**:
   ```bash
   make lint
   make format
   ```

5. **Database operations**:
   ```bash
   make db-shell     # Access database
   make db-backup    # Backup before major changes
   ```

## 🚀 Deployment

### Production Deployment

1. **Prepare environment**:
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with production values
   ```

2. **Deploy**:
   ```bash
   ENV=production make prod-build
   ```

3. **Enable monitoring**:
   ```bash
   make monitoring
   ```

4. **Setup automated backups**:
   ```bash
   # Backups run automatically via cron in production
   # Check backup logs: make logs | grep backup
   ```

### Scaling

For horizontal scaling, modify `docker-compose.prod.yml`:
```yaml
services:
  fastapi:
    deploy:
      replicas: 4  # Scale backend
  frontend:
    deploy:
      replicas: 2  # Scale frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in development environment
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs: `make logs`
3. Open an issue on GitHub
4. Check existing documentation

## 🎉 What's New in This Version

- **Multi-stage Docker builds** for 60% smaller production images
- **Enhanced security** with non-root users and read-only containers
- **Advanced caching** with Nginx cache zones and Redis integration
- **Comprehensive monitoring** with Prometheus and Grafana
- **Automated backups** with configurable retention
- **Production-ready** SSL, security headers, and rate limiting
- **Developer experience** improvements with hot reloading and debugging tools
- **Performance optimizations** with tuned database settings and connection pooling 