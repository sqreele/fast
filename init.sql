-- Initialize the PM system database
-- This script runs when the PostgreSQL container starts for the first time

-- The database pm_database is already created by POSTGRES_DB environment variable
-- We just need to set up the permissions and any additional configuration

-- Grant privileges to the user (database already exists)
GRANT ALL PRIVILEGES ON DATABASE pm_database TO pm_user;
ALTER DATABASE pm_database OWNER TO pm_user;

-- Connect to the pm_database
\c pm_database;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO pm_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pm_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pm_user; 