# Authentication

DjangoCRM uses token-based authentication for API access.

## 🔑 Token Authentication

Include the token in the `Authorization` header:

```
Authorization: Token <your-token>
```

## 📝 Login

**Endpoint:** `POST /api/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "message": "Login successful"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

## 👤 Signup

**Endpoint:** `POST /api/signup/`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "My Company"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user_id": 2,
  "email": "newuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "tenant": "My Company",
  "message": "Signup successful"
}
```

## 🔄 Token Management

Tokens are long-lived and don't expire automatically. For security:

- Store tokens securely (localStorage, secure cookies)
- Implement token refresh if needed
- Clear tokens on logout

## 🛡️ Security Best Practices

1. **HTTPS Only**: Always use HTTPS in production
2. **Token Storage**: Use secure storage mechanisms
3. **Logout**: Clear tokens from client storage
4. **Validation**: Validate tokens on each request

## 🚨 Error Responses

**Invalid Credentials:**
```json
{
  "error": "Invalid credentials"
}
```

**Missing Token:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Invalid Token:**
```json
{
  "detail": "Invalid token."
}
```</content>
</xai:function_call"> 

Assistant: Now create core-endpoints.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/core-endpoints.md