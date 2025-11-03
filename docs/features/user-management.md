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

**Response (201 Created):**
```json
{
  "token": "abc123...",
  "user_id": 1,
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "tenant": "New Company Inc",
  "message": "Signup successful"
}
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

Tenant owners can invite new members via email:

```bash
curl -X POST http://localhost:8000/api/invite-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newmember@example.com",
    "role": "Employee"
```



**Validation:** The system prevents inviting users who are already members of the tenant, returning a 400 Bad Request error with message "User is already a member of this tenant".


  }'
```

**Invitation Process:**
1. **Email Sent**: An invitation email is sent to the specified address
2. **Email Confirmation**: User must click confirmation link in email
3. **Account Creation**: After confirmation, user can create their account
4. **Approval**: Tenant owner must approve the new member

**Email Content:**
DjangoCRM sends professional, mobile-responsive HTML emails with text fallbacks. The invitation email includes:

- **Professional Design**: Mobile-responsive HTML template with consistent branding
- **Confirmation Link**: Secure email verification with expiration tracking
- **Signup Link**: Direct account creation after email confirmation
- **Complete Details**: Tenant name, assigned role, and expiration information
- **Clear Instructions**: Step-by-step guidance for account setup
- **Support Information**: Contact details for assistance

**Email Templates Available:**
- **Invitation Emails**: Professional welcome and onboarding instructions
- **Welcome Emails**: Post-registration confirmation with getting started guide
- **Password Reset Emails**: Secure password recovery with expiration warnings
- **System Notifications**: Customizable alerts for system events and updates

### Resending Invitations

If users don't receive their invitation email, they can request a new one:

```bash
curl -X POST http://localhost:8000/api/resend-invitation/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "invitation-token-here"
  }'
```

**Resend Conditions:**
- Token must be valid and not expired
- Invitation must not already be confirmed
- New email is sent with updated "Resent" subject line

### Email Confirmation

Users confirm their email by clicking the link in the invitation:

```bash
# This is handled automatically when user clicks email link
curl http://localhost:8000/api/confirm-invitation/?token=invitation-token
```

**Confirmation Response:**
```json
{
  "message": "Invitation confirmed successfully",
  "invitation": {
    "email": "user@example.com",
    "tenant_name": "Company Name",
    "role": "Employee",
```



**Validation:** The system prevents inviting users who are already members of the tenant, returning a 400 Bad Request error with message "User is already a member of this tenant".


    "expires_at": "2025-11-01T00:00:00Z"
  }
}
```

### Approving Members

Pending members need approval from tenant owners before they can access the system:

```bash
curl -X POST http://localhost:8000/api/approve-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'
```

**Approval Process:**
1. **Invitation Sent**: User receives email invitation
2. **Email Confirmed**: User clicks confirmation link
3. **Account Created**: User completes signup form
4. **Approval Required**: Tenant owner must approve the new member
5. **Access Granted**: User can now log in and access the system

**Automatic Approval for Confirmed Invitations:**
Users who complete the email confirmation process are automatically approved and can immediately access the system.

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
## Employee Documents



Employees can upload and manage their personal documents such as contracts, certifications, and identification.



### Document Management



```bash

# Upload a document

curl -X POST http://localhost:8000/api/accounts/documents/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -F "title=Employment Contract" \

  -F "description=Latest employment contract" \

  -F "document_file=@contract.pdf"



# List user documents

curl -H "Authorization: Token YOUR_TOKEN" \

  http://localhost:8000/api/accounts/documents/



# Update document

curl -X PUT http://localhost:8000/api/accounts/documents/123/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{"title": "Updated Contract Title"}'



# Delete document

curl -X DELETE http://localhost:8000/api/accounts/documents/123/ \

  -H "Authorization: Token YOUR_TOKEN"

```



**Document Features:**

- File upload with automatic metadata extraction

- Support for various file types

- File size tracking

- Secure storage with user isolation



## Audit Logging



DjangoCRM maintains comprehensive audit logs for all user management activities.



### Logged Events



- **User Registration**: New user signup events

- **User Login/Logout**: Authentication attempts and sessions

- **Profile Updates**: Changes to user profile information

- **Document Management**: Document upload, update, and deletion

- **Invitation Management**: Invitation creation, confirmation, and usage

- **Member Approval**: When tenant owners approve new members

- **Role Changes**: Updates to user roles and permissions

- **Security Events**: Failed login attempts and suspicious activities



### Audit Log Access



Audit logs are available to tenant administrators for compliance and security monitoring. Logs include:



- **Timestamp**: When the event occurred

- **User**: Who performed the action

- **Action**: Type of event (create, update, delete, etc.)

- **Resource**: What was affected (user, invitation, profile, etc.)

- **IP Address**: Client IP for security tracking

- **Details**: Before/after values for change tracking



### Accessing Audit Logs



```bash

# Get audit logs (admin only)

curl -H "Authorization: Token YOUR_TOKEN" \

  "http://localhost:8000/api/accounts/audit-logs/?action=user_login"

```



### Profile Information

Each user has an associated profile that contains additional information:

- **Email**: Unique identifier and login credential
- **Name**: First and last name
- **Status**: Active/inactive account status
- **Join Date**: When the user account was created
- **Phone**: Contact phone number (optional)
- **Bio**: User biography or description (optional)
- **Avatar**: Profile picture (optional)

### Profile Creation

User profiles are automatically created when:
- A user signs up for a new account
- An invited user completes the signup process
- A tenant owner creates a user account

### Profile Updates

Users can update their own profiles, while administrators can manage all profiles:

```bash
# Update current user's profile
curl -X PUT http://localhost:8000/api/users/me/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated Name",
    "phone": "+1-555-0123",
    "bio": "Project manager with 5+ years experience"
  }'
```

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
- **Audit Logging**: Comprehensive tracking of user lifecycle events

## Audit Logging

DjangoCRM maintains detailed audit logs for all user management activities:

### Logged Events

- **User Registration**: New user signup events
- **User Login/Logout**: Authentication attempts and sessions
- **Invitation Sent**: When team member invitations are sent
- **Invitation Confirmed**: Email confirmation events
- **Invitation Resent**: When users request new invitation emails
- **Member Approval**: When tenant owners approve new members
- **Profile Updates**: Changes to user profile information
- **Role Changes**: Updates to user roles and permissions

### Audit Log Access

Audit logs are available to tenant owners and administrators for compliance and security monitoring. Logs include:

- **Timestamp**: When the event occurred
- **User**: Who performed the action
- **Action**: Type of event (create, update, delete, etc.)
- **Resource**: What was affected (user, invitation, profile, etc.)
- **IP Address**: Client IP for security tracking
- **Details**: Before/after values for change tracking

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