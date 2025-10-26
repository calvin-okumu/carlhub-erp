# User Management

Users are the individuals who interact with DjangoCRM, including team members, managers, and administrators. The system supports multi-tenant user management with role-based access control.

## User Authentication

### Login

Users authenticate using email and password:

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "token": "abc123...",
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "message": "Login successful"
}
```

### Signup

New users can register, optionally joining an existing tenant:

```bash
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "Jane",
    "last_name": "Smith",
    "company_name": "New Company Inc",
    "invitation_token": "optional-invitation-token"
  }'
```

## User Roles and Permissions

### Roles

- **Tenant Owner**: Full administrative access to tenant
- **Manager**: Project management and team oversight
- **Employee**: Standard user with task execution permissions
- **Client**: Limited access to their projects (future feature)

### Permissions

Users have granular permissions for different operations:

- **Project Management**: Create, update, delete projects
- **Task Management**: Assign and update tasks
- **Client Management**: Manage client relationships
- **Invoice Management**: Handle billing and payments
- **User Management**: Invite and manage team members

## User CRUD Operations

### List Users

```bash
# Get all users (admin only)
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/users/
```

### Get User Profile

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/users/123/
```

### Update Profile

```bash
curl -X PUT http://localhost:8000/api/users/123/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated Name",
    "last_name": "Updated Last Name"
  }'
```

## Tenant Membership

### Inviting Members

Tenant owners can invite new members:

```bash
curl -X POST http://localhost:8000/api/invite-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newmember@example.com",
    "role": "Employee"
  }'
```

### Approving Members

Pending members need approval from tenant owners:

```bash
curl -X POST http://localhost:8000/api/approve-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'
```

### Member Management

```bash
# List tenant members
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/members/

# Update member role
curl -X PUT http://localhost:8000/api/members/456/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "Manager"}'
```

## User Profiles

### Profile Information

- **Email**: Unique identifier and login credential
- **Name**: First and last name
- **Status**: Active/inactive account status
- **Join Date**: When the user account was created

### Profile Updates

Users can update their own profiles, while administrators can manage all profiles.

## Authentication Methods

### Available Methods

```bash
curl http://localhost:8000/api/auth-methods/
```

Response:
```json
{
  "traditional": {
    "endpoint": "/api/login/",
    "method": "POST",
    "description": "Email and password authentication",
    "fields": ["email", "password"]
  },
  "oauth": {
    "providers": {
      "google": {
        "login_url": "/accounts/google/login/",
        "description": "Login with Google account"
      },
      "github": {
        "login_url": "/accounts/github/login/",
        "description": "Login with GitHub account"
      }
    }
  }
}
```

## Security Features

### Access Control

- **Tenant Isolation**: Users can only access their tenant's data
- **Role-Based Permissions**: Actions restricted by user role
- **Token Authentication**: Secure API access with tokens
- **Profile Privacy**: Users can only view/modify their own profiles

### Account Security

- **Password Requirements**: Secure password policies
- **Account Locking**: Protection against brute force attacks
- **Session Management**: Automatic token expiration
- **Audit Logging**: Track user actions and changes

## User Groups

Users are automatically assigned to Django groups based on their role:

- **Tenant Owners**: Full administrative permissions
- **Project Managers**: Project and team management permissions
- **Employees**: Standard operational permissions

## Best Practices

### User Onboarding

1. **Clear Roles**: Assign appropriate roles during invitation
2. **Permission Training**: Educate users on their access levels
3. **Profile Completion**: Encourage complete profile information
4. **Security Training**: Teach secure authentication practices

### Account Management

1. **Regular Reviews**: Audit user access periodically
2. **Role Updates**: Adjust roles as responsibilities change
3. **Inactive Accounts**: Deactivate unused accounts
4. **Security Monitoring**: Watch for suspicious activity

### Team Collaboration

1. **Clear Communication**: Define team roles and responsibilities
2. **Access Transparency**: Make permissions clear to all users
3. **Support Structure**: Provide help for permission-related issues
4. **Feedback Collection**: Gather user experience feedback</content>
</xai:function_call">  
</xai:function_call name="todowrite">
<parameter name="todos">[{"content":"Compare task-management.md against actual implementation and update","status":"completed","priority":"high","id":"validate_task_docs"},{"content":"Analyze task-related models, views, and serializers for task-management.md validation","status":"completed","priority":"high","id":"analyze_task_components"},{"content":"Analyze user/account models and views for user-management.md validation","status":"completed","priority":"high","id":"analyze_user_components"},{"content":"Compare user-management.md against actual user implementation and update","status":"completed","priority":"high","id":"validate_user_docs"},{"content":"Analyze multi-tenancy implementation for multi-tenancy.md validation","status":"in_progress","priority":"medium","id":"analyze_multi_tenancy"}]