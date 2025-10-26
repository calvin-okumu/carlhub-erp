# API Reference

This section provides comprehensive documentation for the DjangoCRM REST API.

## 📋 Table of Contents

- [Authentication](./authentication.md)
- [Core Endpoints](./core-endpoints.md)
- [Pagination](./pagination.md)
- [Filtering & Search](./filtering-search.md)
- [Error Handling](./error-handling.md)

## 🌐 Base URL

```
http://localhost:8000/api
```

## 🔐 Authentication

All API requests require authentication using Token Authentication:

```bash
Authorization: Token <your-token>
```

### Getting a Token

1. **Login via API:**
   ```bash
   POST /api/login/
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. **Use token in subsequent requests:**
   ```bash
   GET /api/projects/
   Headers: Authorization: Token abc123...
   ```

## 📊 Response Format

All responses follow a consistent JSON structure:

```json
{
  "id": "uuid",
  "name": "Example Name",
  "slug": "example-name",
  "created_at": "2025-10-19T10:00:00Z",
  "updated_at": "2025-10-19T10:00:00Z"
}
```

## 🏷️ URL Structure

- **Projects**: `/api/projects/{slug}/` (slug-based URLs)
- **Clients**: `/api/clients/{slug}/` (slug-based URLs)
- **Other entities**: `/api/{resource}/{id}/` (ID-based URLs)

Slugs are auto-generated from names but can be customized for better readability.

## 📖 Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🚀 Quick Examples

### List Projects
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/
```

### Get Project Details
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/my-project-slug/
```

### Create a Project
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Project", "client": "client-uuid"}' \
  http://localhost:8000/api/projects/
```</content>
</xai:function_call"> 

Assistant: Now create the authentication.md file. I need to check how authentication works in the backend. From earlier, it's TokenAuthentication. Let me create the file. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/authentication.md