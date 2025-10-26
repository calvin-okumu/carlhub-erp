# Error Handling

Comprehensive error handling guide for DjangoCRM API.

## 📊 HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content returned |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## 🚨 Common Error Responses

### Authentication Errors

**401 Unauthorized - Missing Token:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 Unauthorized - Invalid Token:**
```json
{
  "detail": "Invalid token."
}
```

**401 Unauthorized - Invalid Credentials:**
```json
{
  "error": "Invalid credentials"
}
```

### Validation Errors

**400 Bad Request - Field Validation:**
```json
{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."]
}
```

**400 Bad Request - Business Logic:**
```json
{
  "error": "End date must be after start date."
}
```

**409 Conflict - Duplicate Resource:**
```json
{
  "slug": ["A project with this slug already exists."]
}
```

### Permission Errors

**403 Forbidden - Insufficient Permissions:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**403 Forbidden - Tenant Access:**
```json
{
  "detail": "You can only access resources in your tenant."
}
```

### Not Found Errors

**404 Not Found - Resource Not Found:**
```json
{
  "detail": "Not found."
}
```

**404 Not Found - Invalid Slug:**
```json
{
  "detail": "No Project matches the given query."
}
```

## 🔧 Error Handling Patterns

### JavaScript/Fetch
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

      // Handle specific error types
      switch (response.status) {
        case 401:
          // Token expired or invalid
          handleAuthError(errorData);
          break;
        case 403:
          // Permission denied
          showPermissionError(errorData);
          break;
        case 404:
          // Resource not found
          showNotFoundError(errorData);
          break;
        case 422:
          // Validation errors
          showValidationErrors(errorData);
          break;
        default:
          // Generic error
          showGenericError(errorData);
      }

      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

// Usage
try {
  const project = await apiRequest('/api/projects/my-project/');
  console.log('Project:', project);
} catch (error) {
  // Error already handled above
}
```

### React Error Boundary
```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    // Log to error reporting service
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

// Wrap your app
function App() {
  return (
    <ErrorBoundary>
      <ProjectProvider>
        {/* Your app components */}
      </ProjectProvider>
    </ErrorBoundary>
  );
}
```

### React Hook for API Calls
```jsx
import { useState, useCallback } from 'react';

function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const makeRequest = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        const error = new Error(
          errorData.detail ||
          errorData.error ||
          `HTTP ${response.status}: ${response.statusText}`
        );
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      const data = await response.json();
      return data;
    } catch (error) {
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return { makeRequest, loading, error };
}

// Usage in component
function ProjectList() {
  const { makeRequest, loading, error } = useApi();
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await makeRequest('/api/projects/');
        setProjects(data.results || data);
      } catch (err) {
        // Error is already set in hook
        console.error('Failed to fetch projects:', err);
      }
    };

    fetchProjects();
  }, [makeRequest]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {projects.map(project => (
        <div key={project.id}>{project.name}</div>
      ))}
    </div>
  );
}
```

## 🔄 Retry Logic

### Exponential Backoff
```javascript
async function apiRequestWithRetry(url, options = {}, maxRetries = 3) {
  let attempt = 0;

  while (attempt < maxRetries) {
    try {
      return await apiRequest(url, options);
    } catch (error) {
      attempt++;

      // Don't retry on client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt >= maxRetries) {
        throw error;
      }

      // Exponential backoff: 1s, 2s, 4s...
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

## 📱 User-Friendly Error Messages

### Error Message Mapping
```javascript
const ERROR_MESSAGES = {
  400: 'Invalid request. Please check your input.',
  401: 'Please log in to continue.',
  403: 'You don\'t have permission to perform this action.',
  404: 'The requested resource was not found.',
  409: 'This action would create a conflict. Please try again.',
  422: 'Please correct the errors and try again.',
  429: 'Too many requests. Please wait a moment.',
  500: 'Server error. Please try again later.',
};

function getUserFriendlyMessage(error) {
  if (error.data) {
    // Handle field-specific validation errors
    if (typeof error.data === 'object') {
      const fieldErrors = Object.entries(error.data)
        .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
        .join('; ');
      return fieldErrors || ERROR_MESSAGES[error.status] || 'An error occurred.';
    }
  }

  return ERROR_MESSAGES[error.status] || error.message || 'An unexpected error occurred.';
}
```

### Toast Notifications
```jsx
import { toast } from 'react-toastify';

function handleApiError(error) {
  const message = getUserFriendlyMessage(error);

  toast.error(message, {
    position: "top-right",
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  });
}

// Usage
try {
  await apiRequest('/api/projects/');
} catch (error) {
  handleApiError(error);
}
```

## 🐛 Debugging API Errors

### Enable Debug Logging
```javascript
// Add to your API client
const DEBUG = process.env.NODE_ENV === 'development';

function logApiCall(url, options, response, error = null) {
  if (!DEBUG) return;

  console.group(`API Call: ${options.method || 'GET'} ${url}`);
  console.log('Request:', options);
  console.log('Response:', response);
  if (error) console.error('Error:', error);
  console.groupEnd();
}
```

### Network Tab Inspection
1. Open browser DevTools → Network tab
2. Make the failing API call
3. Check the request/response details
4. Look for CORS issues, missing headers, or malformed data

### Common Debugging Steps
1. **Check token validity:** Ensure token hasn't expired
2. **Verify permissions:** Confirm user has required permissions
3. **Validate data:** Check request body format and required fields
4. **Check network:** Ensure API server is accessible
5. **Review logs:** Check server logs for detailed error information

## 📞 Getting Help

If you encounter persistent errors:

1. **Check the API documentation:** http://localhost:8000/api/schema/swagger-ui/
2. **Review server logs:** Check backend logs for detailed error traces
3. **Validate request format:** Compare with working examples
4. **Test with curl:** Isolate frontend issues by testing directly with curl
5. **Open an issue:** Include full error details, request/response, and steps to reproduce</content>
</xai:function_call"> 

Assistant: Now I need to update the docs/README.md to remove the references to non-existent files and update the structure. Also, check if there are other docs that need updating.

Let me check the features/ folder. 

<xai:function_call name="list">
<parameter name="path">docs/features