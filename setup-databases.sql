-- Setup script for DjangoCRM microservices databases
-- Run this to create user and databases for all services

-- Create user
CREATE USER django_microservices WITH PASSWORD 'django_microservices';

-- Create databases
CREATE DATABASE identity_db OWNER django_microservices;
CREATE DATABASE audit_db OWNER django_microservices;
CREATE DATABASE notification_db OWNER django_microservices;
CREATE DATABASE accounting_db OWNER django_microservices;
CREATE DATABASE hr_db OWNER django_microservices;
CREATE DATABASE project_db OWNER django_microservices;
CREATE DATABASE sales_db OWNER django_microservices;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE identity_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE audit_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE hr_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE project_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO django_microservices;

-- Show created databases
\l

-- Show user
\du
