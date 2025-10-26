# Authentication

DjangoCRM uses Token-based authentication for API access. All API requests require a valid authentication token.

## 🔐 Authentication Methods

### Token Authentication

DjangoCRM uses Django REST Framework's Token Authentication system.

#### Getting a Token

**Endpoint:** `POST /api/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tenant": {
    "id": "uuid",
    "name": "Company Name"
  }
}
```

**Example:**
```bash
curl -X POST \
  http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

#### Using the Token

Include the token in the `Authorization` header for all subsequent requests:

```
Authorization: Token abc123def456...
```

**Example:**
```bash
curl -H "Authorization: Token abc123def456..." \
  http://localhost:8000/api/projects/
```

## 👥 User Invitations

### Inviting Team Members

Tenant owners can invite new team members via email:

**Endpoint:** `POST /api/invite-member/`

**Request Body:**
```json
{
  "email": "newmember@example.com",
  "role": "Employee"
}
```

**Response:**
```json
{
  "message": "Invitation sent successfully",
  "token": "invitation-token-here"
}
```

**Example:**
```bash
curl -X POST \
  http://localhost:8000/api/invite-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "role": "Employee"}'
```

### Email Confirmation

Users must confirm their email before creating an account:

**Endpoint:** `GET /api/confirm-invitation/?token=<token>`

**Response:**
```json
{
  "message": "Invitation confirmed successfully",
  "invitation": {
    "email": "user@example.com",
    "tenant_name": "Company Name",
    "role": "Employee",
    "expires_at": "2025-11-01T00:00:00Z"
  }
}
```

### Resending Invitations

If users don't receive their invitation email, they can request a new one:

**Endpoint:** `POST /api/resend-invitation/`

**Request Body:**
```json
{
  "token": "original-invitation-token"
}
```

**Response:**
```json
{
  "message": "Invitation email resent successfully"
}
```

**Example:**
```bash
curl -X POST \
  http://localhost:8000/api/resend-invitation/ \
  -H "Content-Type: application/json" \
  -d '{"token": "abc123..."}'
```

### Approving Team Members

Tenant owners must approve new members before they can access the system:

**Endpoint:** `POST /api/approve-member/`

**Request Body:**
```json
{
  "user_id": 123
}
```

**Response:**
```json
{
  "message": "Member approved successfully"
}
```

**Example:**
```bash
curl -X POST \
  http://localhost:8000/api/approve-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'
```

### User Signup

After email confirmation, users can create their account:

**Endpoint:** `POST /api/signup/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "invitation_token": "invitation-token-here"
}
```

**Response:**
```json
{
  "token": "user-auth-token",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tenant": {
    "id": 456,
    "name": "Company Name"
  }
}
```

### Session Authentication

For web interface access, DjangoCRM also supports session-based authentication through the Django admin and frontend application.

## 👥 User Roles & Permissions

DjangoCRM implements role-based access control with the following roles:

- **Tenant Owner**: Full access to all tenant resources
- **Manager**: Can manage projects, clients, and team members
- **Employee**: Can view and update assigned tasks and projects
- **Client**: Limited access to their own projects and invoices

### Permission Matrix

| Resource | Tenant Owner | Manager | Employee | Client |
|----------|-------------|---------|----------|--------|
| Projects | CRUD | CRUD | R/Update | Read (own) |
| Clients | CRUD | CRUD | Read | Read (own) |
| Tasks | CRUD | CRUD | CRUD (assigned) | Read (own projects) |
| Invoices | CRUD | CRUD | Read | Read (own) |
| Users | CRUD | Manage team | Read | None |

## 🔒 Security Features

### Multi-Tenant Isolation
- Complete data isolation between tenants
- Row-level security on all database queries
- Tenant context enforced on all operations

### Token Security
- Tokens are cryptographically secure random strings
- Tokens can be revoked individually
- Automatic token expiration (configurable)

### Request Security
- CSRF protection on state-changing operations
- Rate limiting on authentication endpoints
- Input validation and sanitization

## 🚪 Logout

To logout and invalidate a token:

**Endpoint:** `POST /api/logout/`

**Headers:** `Authorization: Token <token>`

**Response:** `204 No Content`

Note: Token-based authentication doesn't have true "logout" - simply discard the token on the client side. The `/api/logout/` endpoint is provided for consistency with session-based auth.

## 🔄 Token Management

### Check Token Validity

**Endpoint:** `GET /api/auth-methods/`

**Response:**
```json
{
  "token_auth": true,
  "session_auth": true,
  "oauth_providers": ["google", "github"]
}
```

### Refresh Token (if implemented)

Some deployments may include token refresh functionality. Check with your specific installation.

## 🐛 Troubleshooting Authentication

### Common Issues

**"Authentication credentials were not provided"**
- Missing `Authorization` header
- Incorrect header format (must be `Token <token>`)

**"Invalid token"**
- Token has expired
- Token was revoked
- User account was deactivated

**"Permission denied"**
- User lacks required permissions for the operation
- Attempting to access resources from another tenant

### Debug Authentication

```bash
# Test token validity
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/health/

# Check user permissions
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/users/me/
```

## 📚 Related Documentation

- [Core Endpoints](./core-endpoints.md) - Main API resources
- [Error Handling](./error-handling.md) - Authentication error responses</content>
</xai:function_call"> 

Assistant: Now create the core-endpoints.md file. This should document the main API endpoints. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/core-endpoints.md