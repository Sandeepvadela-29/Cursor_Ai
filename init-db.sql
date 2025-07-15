-- TrueFit Platform Database Initialization Script
-- This script sets up the initial database structure and configurations

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create indexes for better performance (will be created by Alembic migrations)
-- But we can set up some initial configurations

-- Set timezone
SET timezone = 'UTC';

-- Create a function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE truefit_db TO truefit;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO truefit;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO truefit;

-- Create initial admin user (will be handled by application)
-- This is just a placeholder comment for future admin setup