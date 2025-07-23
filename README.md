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

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - API: http://localhost
   - API Documentation: http://localhost/docs
   - Admin Dashboard: http://localhost/api/v1/admin/health
   - Health Check: http://localhost/health

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