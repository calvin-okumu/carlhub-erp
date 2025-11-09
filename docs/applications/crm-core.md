# CRM Core

The foundation application of DjangoCRM providing essential customer relationship management, user management, and system administration capabilities.

## Core Features

### User Management
- Multi-tenant user registration and authentication
- Role-based access control (Owner, Manager, Employee, Client)
- User profile management with extended information
- Employee document storage and management

### Client Management
- Client relationship database
- Contact information and company details
- Client status tracking (Active, Inactive, Prospect)
- Client history and interaction logging

### System Administration
- Tenant management and configuration
- System-wide settings and preferences
- User permission and role assignment
- Audit logging and compliance tracking

## Architecture

### Data Models
- **CustomUser**: Extended Django user with soft delete
- **Tenant**: Multi-tenant organization container
- **UserTenant**: User-tenant membership relationships
- **Client**: Customer/organization records
- **UserProfile**: Extended user information
- **EmployeeDocument**: Document storage for employees

### Key Components
- **Authentication System**: JWT-based API authentication
- **Permission Framework**: Custom permission groups and assignments
- **Audit System**: Comprehensive logging of all user actions
- **Email Service**: Professional email templates and delivery

## API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/signup/` - User registration
- `GET /api/auth-methods/` - Available auth methods

### User Management
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile

### Client Management
- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client
- `PUT /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client

### Invitations
- `POST /api/invite-member/` - Invite new member
- `POST /api/resend-invitation/` - Resend invitation
- `POST /api/confirm-invitation/` - Confirm email
- `GET /api/invitations/` - List invitations

## Security Features

### Data Isolation
- Complete tenant data separation
- Row-level security on all queries
- Permission-based access control

### Audit Trail
- All user actions logged
- IP address tracking
- Timestamp recording
- Compliance reporting

### Authentication
- Secure password hashing
- JWT token management
- Session timeout handling
- Failed login monitoring

## Integration Points

### Project Tracker
- User data synchronization
- Client data sharing
- Permission inheritance

### Financial Suite
- User access to financial data
- Client billing information
- Invoice permissions

### Admin Panel
- User management interface
- System configuration
- Audit log access