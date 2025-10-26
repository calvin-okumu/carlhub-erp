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

```
Authorization: Token <your-token>
```

Get a token by logging in via `/login/` endpoint.

## 📊 Response Format

All responses are in JSON format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

## 🚀 Quick Start

```bash
# 1. Get authentication token
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# 2. Use token for authenticated requests
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/projects/
```

## 📚 Interactive Documentation

For detailed API exploration, visit:
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

## 🏗️ Architecture

The API follows REST principles with the following key features:

- **Multi-tenant**: Automatic data isolation by tenant
- **Role-based permissions**: Access control based on user roles
- **Slug-based URLs**: Human-readable identifiers for resources
- **Comprehensive filtering**: Advanced query capabilities
- **Progress tracking**: Automated project progress calculation</content>
</xai:function_call"> 

Assistant: Now create the authentication.md file. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/authentication.md