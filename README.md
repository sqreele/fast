# PM System API

A comprehensive Preventive Maintenance (PM) System built with FastAPI and PostgreSQL.

## Features

- **User Management**: Role-based access control (Technician, Supervisor, Manager, Admin)
- **Property & Room Management**: Organize equipment by location
- **Machine Tracking**: Complete equipment inventory and maintenance history
- **PM Scheduling**: Automated preventive maintenance scheduling
- **Issue Management**: Track and resolve maintenance issues
- **Inspections**: Conduct and document equipment inspections
- **File Management**: Attach files to PMs, issues, and inspections
- **Admin Dashboard**: Comprehensive system administration tools

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Auto-generated with FastAPI

## Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd Fast_api
   ```

2. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env file with your preferred settings
   ```

3. **Start the application:**
   
   **For Development:**
   ```bash
   ./docker-manage.sh dev
   # OR manually:
   docker-compose up --build
   ```
   
   **For Production:**
   ```bash
   ./docker-manage.sh prod
   # OR manually:
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
   ```

4. **Access the application:**
   - **Development:**
     - Frontend: http://localhost:3000
     - Backend API: http://localhost:8000
     - API Documentation: http://localhost:8000/docs
     - Database Admin (Adminer): http://localhost:8081
     - Nginx Proxy: http://localhost
   - **Production:**
     - Application: http://localhost
     - API Documentation: http://localhost/docs
     - Database Admin: http://localhost:8081

### Docker Management Commands

Use the included management script for common operations:

```bash
./docker-manage.sh dev      # Start development environment
./docker-manage.sh prod     # Start production environment
./docker-manage.sh stop     # Stop all containers
./docker-manage.sh clean    # Clean up containers and volumes
./docker-manage.sh logs     # View container logs
./docker-manage.sh db-shell # Connect to PostgreSQL database
```

## Database Configuration

### PostgreSQL Setup

The application uses PostgreSQL as the primary database. The Docker setup includes:

- **PostgreSQL 15** container with persistent data storage
- **Adminer** web interface for database management
- **Automatic initialization** with proper user permissions
- **Health checks** to ensure database availability

### Database Connection

**Environment Variables:**
```bash
DATABASE_URL=postgresql://pm_user:pm_password@pm_postgres_db:5432/pm_database
POSTGRES_DB=pm_database
POSTGRES_USER=pm_user
POSTGRES_PASSWORD=pm_password
```

**Database Access:**
- **Adminer Web Interface**: http://localhost:8081
  - Server: `pm_postgres_db`
  - Username: `pm_user`
  - Password: `pm_password`
  - Database: `pm_database`

- **Direct Connection**: 
  ```bash
  ./docker-manage.sh db-shell
  # OR manually:
  docker-compose exec pm_postgres_db psql -U pm_user -d pm_database
  ```

### Database Management

**Backup Database:**
```bash
docker-compose exec pm_postgres_db pg_dump -U pm_user pm_database > backup.sql
```

**Restore Database:**
```bash
docker-compose exec -T pm_postgres_db psql -U pm_user pm_database < backup.sql
```

**Reset Database:**
```bash
./docker-manage.sh clean  # This will remove all data
./docker-manage.sh dev    # Restart with fresh database
```

### Local Development

1. **Set up Python environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   # For development (creates tables directly)
   python init_db.py
   
   # For production (uses migrations)
   python manage_migrations.py init
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /docs` - Interactive API documentation

### User Management
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{id}` - Get specific user
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Admin Endpoints
- `GET /api/v1/admin/stats` - System statistics
- `POST /api/v1/admin/setup` - Initial system setup
- `GET /api/v1/admin/health` - System health check
- `POST /api/v1/admin/cleanup/files` - Clean old files
- `POST /api/v1/admin/users/deactivate-inactive` - Deactivate inactive users

### Migration Endpoints
- `GET /api/v1/migrations/status` - Get migration status
- `GET /api/v1/migrations/history` - Get migration history
- `POST /api/v1/migrations/upgrade` - Upgrade database
- `POST /api/v1/migrations/downgrade` - Downgrade database
- `POST /api/v1/migrations/create` - Create new migration
- `POST /api/v1/migrations/stamp` - Stamp database revision

## Database Schema

### Core Entities
- **Users**: System users with role-based access
- **Properties**: Physical locations/facilities
- **Rooms**: Rooms within properties
- **Machines**: Equipment requiring maintenance
- **Topics**: Maintenance categories
- **Procedures**: Maintenance procedures and instructions

### Maintenance Entities
- **PM Schedules**: Scheduled maintenance tasks
- **PM Executions**: Actual maintenance performed
- **Issues**: Problems requiring attention
- **Inspections**: Equipment inspections
- **PM Files**: Attachments for maintenance records

## Default Data

The system automatically creates:
- Admin user: `admin` / `admin@pmsystem.com`
- Default maintenance topics (Preventive, Corrective, Inspection, etc.)
- Sample maintenance procedures

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./pm_system.db` |
| `DEBUG` | Enable debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Docker Configuration

### Services
- **nginx**: Reverse proxy and load balancer
- **fastapi**: Main application server
- **postgres**: PostgreSQL database
- **networks**: Isolated network for services
- **volumes**: Persistent database and log storage

### Ports
- **80**: Nginx (HTTP)
- **443**: Nginx (HTTPS)
- **15432**: PostgreSQL database (mapped from container port 5432)

## Database Migrations

The system uses Alembic for database migrations, allowing safe schema changes in production.

### Migration Commands

#### **Local Development:**
```bash
# Create initial migration
python manage_migrations.py init

# Create new migration
python manage_migrations.py create "Add new table"

# Apply migrations
python manage_migrations.py upgrade

# Downgrade migration
python manage_migrations.py downgrade -1

# Show migration history
python manage_migrations.py history

# Show current status
python manage_migrations.py current
```

#### **Docker Environment:**
```bash
# Create initial migration
./docker-migrate.sh init

# Create new migration
./docker-migrate.sh create "Add new table"

# Apply migrations
./docker-migrate.sh upgrade

# Show migration history
./docker-migrate.sh history
```

#### **API Endpoints:**
```bash
# Get migration status
curl http://localhost/api/v1/migrations/status

# Get migration history
curl http://localhost/api/v1/migrations/history

# Upgrade database
curl -X POST http://localhost/api/v1/migrations/upgrade

# Create new migration
curl -X POST http://localhost/api/v1/migrations/create \
  -H "Content-Type: application/json" \
  -d '{"message": "Add new table"}'
```

### Migration Workflow

1. **Development**: Make changes to models in `models/models.py`
2. **Create Migration**: Generate migration file with changes
3. **Review**: Check generated migration in `migrations/versions/`
4. **Apply**: Run migration to update database
5. **Test**: Verify changes work correctly

## Development

### Project Structure
```
backend/
├── models/              # Database models
├── routes/              # API routes
├── migrations/          # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py           # Migration environment
│   └── script.py.mako   # Migration template
├── admin.py             # Admin utilities
├── database.py          # Database configuration
├── main.py              # FastAPI application
├── init_db.py           # Database initialization
├── manage_migrations.py # Migration management script
├── docker-migrate.sh    # Docker migration script
├── alembic.ini          # Alembic configuration
└── requirements.txt     # Python dependencies
```

### Adding New Features
1. Create models in `models/models.py`
2. Add Pydantic schemas in `models/`
3. Create routes in `routes/`
4. Create database migration: `python manage_migrations.py create "Description"`
5. Apply migration: `python manage_migrations.py upgrade`
6. Update admin functions if needed
7. Test with Docker Compose

## Production Deployment

1. **Set production environment variables:**
   ```bash
   export POSTGRES_PASSWORD=your_secure_password
   export DATABASE_URL=postgresql://pm_user:your_secure_password@localhost:15432/pm_system
   export DEBUG=False
   export ENVIRONMENT=production
   ```

2. **Run database migrations:**
   ```bash
   # Using Docker
   ./docker-migrate.sh init
   
   # Or locally
   python manage_migrations.py init
   python manage_migrations.py upgrade
   ```

3. **Generate SSL certificates (or use Let's Encrypt):**
   ```bash
   # For development (self-signed)
   ./nginx/generate-ssl.sh
   ```

## Troubleshooting

### Common Issues

**Database Connection Failed:**
```bash
# Check if PostgreSQL container is running
./docker-manage.sh logs

# Reset database if corrupted
./docker-manage.sh clean
./docker-manage.sh dev
```

**Port Already in Use:**
```bash
# Find process using the port
sudo lsof -i :8000  # For backend
sudo lsof -i :3000  # For frontend
sudo lsof -i :80    # For nginx

# Stop the conflicting process or change ports in docker-compose.yml
```

**Frontend Build Issues:**
```bash
# Clear npm cache and rebuild
./docker-manage.sh stop
docker-compose build --no-cache frontend
./docker-manage.sh dev
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker-manage.sh
```

**Database Not Initializing:**
```bash
# Check init.sql is properly loaded
./docker-manage.sh db-shell
\l  # List databases
\dt # List tables
```

**Health Check Failures:**
```bash
# Check service logs
./docker-manage.sh logs fastapi
./docker-manage.sh logs frontend
./docker-manage.sh logs pm_postgres_db
```

### Getting Help

- Check container logs: `./docker-manage.sh logs`
- Access database: `./docker-manage.sh db-shell`
- API Documentation: http://localhost:8000/docs (development)
- Database Admin: http://localhost:8081
   
   # For production, place your certificates in nginx/ssl/
   # - cert.pem (certificate)
   # - key.pem (private key)
   ```

4. **Use production Docker Compose:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

5. **Enable HTTPS (uncomment SSL configuration in nginx/nginx.conf)**

## Troubleshooting

### Common Issues

1. **Database connection failed:**
   - Check if PostgreSQL container is running
   - Verify database credentials
   - Check network connectivity

2. **Port already in use:**
   - Change ports in docker-compose.yml
   - Stop conflicting services

3. **Permission denied:**
   - Check file permissions
   - Run with appropriate user privileges

### Logs
```bash
# View application logs
docker-compose logs fastapi

# View database logs
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 