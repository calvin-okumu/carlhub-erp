# Error Handling

DjangoCRM provides consistent error responses across all API endpoints.

## 🛡️ Robust Error Handling Implementation

DjangoCRM implements comprehensive error handling across all API endpoints to ensure reliable operation and consistent user experience.

### Key Features

- **Isolated Audit Logging**: Audit logging failures never break main operations
- **Consistent JSON Responses**: All errors return JSON, never HTML debug pages
- **Detailed Logging**: Server-side logging captures all exceptions for debugging
- **Graceful Degradation**: Services continue functioning even when auxiliary systems fail
- **User-Friendly Messages**: Clear, actionable error messages for end users

### Protected Endpoints

The following critical API endpoints now have comprehensive error handling:

- **Authentication**: `/api/login/`, `/api/signup/`
- **User Management**: `/api/approve-member/`, `/api/invite-member/`
- **Invitations**: `/api/confirm-invitation/`, `/api/resend-invitation/`
- **All ViewSets**: Automatic error handling via Django REST framework

## 📊 HTTP Status Codes

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content returned

### Client Error Codes
- `400 Bad Request` - Invalid request data or parameters
- `401 Unauthorized` - Authentication required or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (duplicate, constraint violation)
- `422 Unprocessable Entity` - Validation failed
- `429 Too Many Requests` - Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error` - Unexpected server error (always returns JSON)
- `502 Bad Gateway` - Gateway error
- `503 Service Unavailable` - Service temporarily unavailable

## 📝 Error Response Format

All error responses follow a consistent JSON structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field_name": ["Specific field error message"],
    "another_field": ["Another error message"]
  },
  "timestamp": "2025-10-19T10:30:00Z"
}
```

### Implementation Pattern

All API views follow this error handling pattern:

```python
logger = logging.getLogger(__name__)
try:
    # Main business logic
    try:
        # Isolated audit logging
        AuditLogger.log_event(...)
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        # Continue with main operation

    return Response({...})
except Exception as e:
    logger.error(f"{view_name} error: {e}")
    return Response({'error': 'Internal server error'}, status=500)
```

This ensures:
- Audit logging failures don't break core functionality
- All exceptions are logged for debugging
- Users always receive JSON responses
- Services remain operational during logging outages

### Validation Error Example

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "name": ["This field is required."],
    "email": ["Enter a valid email address."],
    "budget": ["Ensure this value is greater than or equal to 0."]
  },
  "timestamp": "2025-10-19T10:30:00Z"
}
```

### Authentication Error Example

```json
{
  "error": "Authentication credentials were not provided.",
  "code": "AUTHENTICATION_REQUIRED",
  "details": {},
  "timestamp": "2025-10-19T10:30:00Z"
}
```

### Permission Error Example

```json
{
  "error": "You do not have permission to perform this action.",
  "code": "PERMISSION_DENIED",
  "details": {
    "required_permission": "project.create",
    "user_role": "employee"
  },
  "timestamp": "2025-10-19T10:30:00Z"
}
```

## 🔍 Common Error Scenarios

### Authentication Errors

**Missing Token:**
```json
{
  "error": "Authentication credentials were not provided.",
  "code": "AUTHENTICATION_REQUIRED"
}
```

**Invalid Token:**
```json
{
  "error": "Invalid token.",
  "code": "INVALID_TOKEN"
}
```

**Expired Token:**
```json
{
  "error": "Token has expired.",
  "code": "TOKEN_EXPIRED"
}
```

### Email Operation Errors

**SMTP Connection Failed:**
```json
{
  "error": "Email service temporarily unavailable. Please try again in a few minutes.",
  "code": "EMAIL_ERROR",
  "details": {
    "operation": "invitation_send",
    "retry_after": 300
  }
}
```

**Email Service Unavailable:**
```json
{
  "error": "Unable to send email. The invitation was created but email delivery failed.",
  "code": "EMAIL_ERROR",
  "details": {
    "operation": "invitation_send",
    "error_type": "smtp_connection_error",
    "fallback": "manual_invitation_url"
  }
}
```

**Note:** Email failures are handled gracefully - user accounts are still created and invitations remain valid even if email delivery fails.

### Validation Errors

**Required Field Missing:**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "name": ["This field is required."]
  }
}
```

**Invalid Format:**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": ["Enter a valid email address."],
    "start_date": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]
  }
}
```

**Unique Constraint Violation:**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": ["Client with this email already exists."],
    "slug": ["Project with this slug already exists."]
  }
}
```

### Permission Errors

**Insufficient Permissions:**
```json
{
  "error": "You do not have permission to perform this action.",
  "code": "PERMISSION_DENIED",
  "details": {
    "resource": "project",
    "action": "delete",
    "required_role": "manager"
  }
}
```

**Tenant Access Denied:**
```json
{
  "error": "Access denied to this tenant's resources.",
  "code": "TENANT_ACCESS_DENIED",
  "details": {
    "requested_tenant": "uuid",
    "user_tenant": "uuid"
  }
}
```

### Resource Errors

**Not Found:**
```json
{
  "error": "Project not found.",
  "code": "NOT_FOUND",
  "details": {
    "resource_type": "project",
    "identifier": "nonexistent-slug"
  }
}
```

**Conflict:**
```json
{
  "error": "Cannot delete project with active tasks.",
  "code": "RESOURCE_CONFLICT",
  "details": {
    "active_tasks_count": 5,
    "resolution": "Complete or reassign all tasks before deletion"
  }
}
```

## 🚨 Rate Limiting

API requests are rate-limited to prevent abuse:

```json
{
  "error": "Request rate exceeded.",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "retry_after": 60,
    "limit": "100 requests per hour",
    "current_usage": "105"
  }
}
```

## 🛠️ Error Handling Best Practices

### Client-Side Error Handling

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json();

      switch (response.status) {
        case 400:
          // Validation error - show field errors
          handleValidationError(errorData);
          break;
        case 401:
          // Authentication error - redirect to login
          handleAuthError(errorData);
          break;
        case 403:
          // Permission error - show permission message
          handlePermissionError(errorData);
          break;
        case 404:
          // Not found - show 404 page
          handleNotFoundError(errorData);
          break;
        case 429:
          // Rate limited - show retry message
          handleRateLimitError(errorData);
          break;
        default:
          // Generic error
          handleGenericError(errorData);
      }

      throw new Error(errorData.error || 'API request failed');
    }

    return await response.json();

  } catch (error) {
    // Network error or other issues
    console.error('API Error:', error);
    throw error;
  }
}
```

### React Error Boundary

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    logError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>Please try refreshing the page</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Form Validation

```javascript
function handleValidationError(errorData) {
  const fieldErrors = errorData.details || {};

  // Clear previous errors
  clearFieldErrors();

  // Show field-specific errors
  Object.keys(fieldErrors).forEach(fieldName => {
    const errors = fieldErrors[fieldName];
    showFieldError(fieldName, errors.join(', '));
  });

  // Show general error message
  showToast(errorData.error, 'error');
}
```

## 🔧 Debugging API Errors

### Enable Debug Mode

For development, enable debug mode to get detailed error information:

```bash
# In settings.py
DEBUG = True
```

### Check Logs

Server logs contain detailed error information:

```bash
# Backend logs
docker-compose logs backend

# Check Django logs
tail -f backend/logs/django.log
```

### API Debug Endpoint

Use the health check endpoint to verify API status:

```bash
curl http://localhost:8000/api/health/
```

### Common Debug Steps

1. **Check request format:**
   ```bash
   curl -v -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/projects/
   ```

2. **Verify token validity:**
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/users/me/
   ```

3. **Check permissions:**
   ```bash
   # Try with different user roles
   curl -H "Authorization: Token ADMIN_TOKEN" \
     http://localhost:8000/api/projects/
   ```

4. **Validate data:**
   ```bash
   # Test with minimal valid data
   curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Project"}' \
     http://localhost:8000/api/projects/
   ```

## 📞 Support

When reporting API errors, include:

- Full request (URL, headers, body)
- Complete response (status code, headers, body)
- User role and permissions
- Steps to reproduce
- Browser/client information
- Server logs (if available)

This helps diagnose issues quickly and provide accurate solutions.</content>
</xai:function_call"> 

Assistant: Now I need to update the main docs/README.md to remove the references to non-existent files and update the structure. 

<xai:function_call name="edit">
<parameter name="filePath">docs/README.md