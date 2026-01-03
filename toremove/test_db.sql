-- Minimal test data for faster CI setup
-- This can be expanded with sample clients, projects, etc.

-- Insert a test tenant
INSERT INTO accounts_tenant (id, name, company_size, industry, phone, created_at) VALUES
(1, 'Test Tenant', '1-10', 'tech', '123-456-7890', NOW()) ON CONFLICT DO NOTHING;

-- Insert a test user
INSERT INTO auth_user (id, username, email, password, is_active, date_joined) VALUES
(1, 'testuser', 'test@example.com', 'pbkdf2_sha256$260000$test', true, NOW()) ON CONFLICT DO NOTHING;

-- Insert user-tenant relation
INSERT INTO accounts_usertenant (id, user_id, tenant_id, role) VALUES
(1, 1, 1, 'admin') ON CONFLICT DO NOTHING;