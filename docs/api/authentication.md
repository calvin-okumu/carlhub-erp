# Authentication

DjangoCRM uses JWT Bearer authentication for API access. All API requests require a valid access token.

## 🔐 JWT Authentication

JWT access and refresh tokens are issued by the Identity Service.

### Login (Get Tokens)

**Direct:** `POST /api/v1/auth/login/`  
**Via gateway:** `POST /api/v1/identity/auth/login/`

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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "tenant_id": "uuid",
    "role": "Tenant Owner"
  }
}
```

**Example (Gateway):**
```bash
curl -X POST \
  http://localhost:8000/api/v1/identity/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

### Using the Access Token

Include the access token in the `Authorization` header for all requests:

```
Authorization: Bearer <access_token>
```

**Example:**
```bash
curl -H "Authorization: Bearer abc123def456..." \
  http://localhost:8000/api/v1/project/projects/
```

### Refresh Access Token

**Direct:** `POST /api/v1/auth/refresh/`  
**Via gateway:** `POST /api/v1/identity/auth/refresh/`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Logout

**Direct:** `POST /api/v1/auth/logout/`  
**Via gateway:** `POST /api/v1/identity/auth/logout/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### Change Password

**Direct:** `POST /api/v1/auth/change-password/`  
**Via gateway:** `POST /api/v1/identity/auth/change-password/`

### Password Reset

**Request reset:** `POST /api/v1/auth/password-reset/`  
**Confirm reset:** `POST /api/v1/auth/password-reset-confirm/`

## 🔒 Security Features

### Multi-Tenant Isolation
- Tenant context enforced on all operations
- Querysets are scoped by tenant in service APIs

### Token Security
- Short-lived access tokens (default 1 hour)
- Refresh tokens can be revoked and rotated

## 🐛 Troubleshooting Authentication

**"Authentication credentials were not provided"**
- Missing `Authorization` header
- Incorrect header format (must be `Bearer <access_token>`)

**"Invalid token"**
- Token has expired
- Token was revoked
- User account was deactivated

### Debug Authentication

```bash
# Test token validity via gateway
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/identity/health/

# Fetch current user profile
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/identity/users/profile/
```

## 📚 Related Documentation

- [Core Endpoints](./core-endpoints.md) - Main API resources
- [Error Handling](./error-handling.md) - Authentication error responses
