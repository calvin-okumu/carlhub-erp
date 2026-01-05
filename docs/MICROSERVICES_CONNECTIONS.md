# Microservices Connection and Communication

How the 7 DjangoCRM microservices connect, authenticate, and communicate with each other.

---

## Overview

**Architectural Principle:** Service Independence with Shared Authentication

Each microservice is **completely independent** with:
- Separate PostgreSQL database
- Separate Python virtualenv
- Own `settings.py` file
- No direct database connections to other services

**Communication happens through:**
1. **JWT Tokens** - For authentication and authorization
2. **HTTP API requests** - For direct service-to-service calls
3. **Event Bus** (Planned, in toremove/) - For async communication

---

## Authentication Flow

### 1. User Login (Identity Service Only)

**Request:**
```bash
POST http://localhost:8001/api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}
```

**Identity Service Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
    "email": "user@example.com",
    "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df",
    "role": "Tenant Owner",
    "is_owner": true,
    "is_approved": true,
    "full_name": "John Doe",
    "is_staff": false,
    "is_superuser": false
  }
}
```

**What Happens in Identity Service:**
```python
# services/identity-service/identity/jwt_tokens.py

class CustomRefreshToken(RefreshToken):
    def for_user(self, user):
        token = super().for_user(user)
        
        # Add custom claims
        token['user_id'] = str(user.id)  # UUID
        token['tenant_id'] = str(user.user_tenant.tenant.id)  # UUID
        token['role'] = user.user_tenant.role
        token['is_owner'] = user.user_tenant.is_owner
        token['is_approved'] = user.user_tenant.is_approved
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['full_name'] = user.full_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['department_id'] = str(user.department_id) if user.department_id else None
        
        return token
```

---

## 2. JWT Token Structure

**Access Token Payload:**
```json
{
  "token_type": "access",
  "exp": 1737612767,
  "iat": 1737611767,
  "jti": "5d30a67-1234-5678-90ab-cdef12345678",
  "user_id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
  "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df",
  "role": "Tenant Owner",
  "is_owner": true,
  "is_approved": true,
  "department_id": null,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "is_staff": false,
  "is_superuser": false
}
```

**All Users Must Belong to at Least One Tenant:**
- Created via UserTenant model linking User → Tenant
- JWT includes `tenant_id` from this relationship
- All other services filter data by `tenant_id`

---

## 3. Other Services Authentication

### How Other Services Validate JWT

**No Database Lookups - User Created from JWT Payload**

**File: `services/<service>/jwt_auth.py`** (one per service)

```python
# services/project-service/jwt_auth.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class SimpleUser:
    """Lightweight user object from JWT token - no DB lookup"""
    
    is_authenticated = True
    is_anonymous = False

    def __init__(self, id, email, tenant_id, role, **kwargs):
        self.id = id
        self.pk = id
        self.email = email
        self.username = email
        self.tenant_id = tenant_id
        self.role = role
        # ... other fields from JWT


class SimpleJWTAuthentication(JWTAuthentication):
    """Validates JWT, creates SimpleUser from payload"""
    
    def get_user(self, validated_token):
        # Extract all user info from JWT token
        user_id = validated_token.get('user_id')
        email = validated_token.get('email')
        tenant_id = validated_token.get('tenant_id')
        role = validated_token.get('role')
        # ... other fields
        
        if not user_id or not email:
            raise AuthenticationFailed('Invalid token')
        
        # Create user object from JWT payload
        return SimpleUser(
            id=user_id,
            email=email,
            tenant_id=tenant_id,
            role=role,
            is_owner=validated_token.get('is_owner'),
            is_approved=validated_token.get('is_approved'),
            # ... all fields from JWT
        )
```

**Service Settings:**
```python
# services/project-service/project_service/settings.py

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'jwt_auth.SimpleJWTAuthentication',  # Use custom auth, no DB lookups
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

**Benefits:**
- ✅ No database query for authentication
- ✅ UUID user IDs work correctly (no integer conversion)
- ✅ Stateless - all user info in JWT
- ✅ Faster authentication
- ✅ Scalable - no shared user DB needed

---

## 4. Service-to-Service Communication

### Direct HTTP API Calls

**Example: Project Service needs Accounting Service data**

**Project Service calls Accounting Service:**
```python
# In Project Service code

import requests
from django.conf import settings

def get_project_invoices(project_id):
    """Fetch invoices for a project from Accounting service"""
    
    # Use JWT from current request
    token = request.META.get('HTTP_AUTHORIZATION').replace('Bearer ', '')
    
    # Call Accounting service
    response = requests.get(
        f"http://localhost:8004/api/v1/invoices/?project_id={project_id}",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch invoices'}
```

**Accounting Service endpoint:**
```python
# services/accounting-service/accounting/views.py

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by project_id if provided
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Also filter by tenant for security
        tenant_id = self.request.user.tenant_id
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset
```

### UUID-Only References

**Services reference each other using UUIDs only:**

| Source Service | References | Field | Destination |
|---------------|------------|-------|-------------|
| Accounting | `project_id` | UUID | Project |
| Accounting | `client_id` | UUID | Project |
| Project | `client_id` | UUID | Project (self) |
| Project | `assignee_id` | UUID | Identity/HR |
| Sales | `assigned_to_id` | UUID | Identity/HR |
| Sales | `customer_id` | UUID | Sales (self) |

**No foreign keys between databases** - Each service has its own PostgreSQL database

---

## 5. Tenant-Based Data Isolation

### How Each Service Filters Data

**Every service uses JWT's tenant_id:**

```python
# Example in Project Service

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get tenant_id from authenticated user's JWT token
        tenant_id = self.request.user.tenant_id
        
        # Filter all data by tenant
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        # Automatically set tenant_id on create
        serializer = self.get_serializer(data=request.data)
        serializer.validated_data['tenant_id'] = request.user.tenant_id
        serializer.validated_data['owner_id'] = request.user.id
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

**Result:** Users only see data from their own tenant

---

## 6. Complete Request Flow

### Example: Frontend Creates a Project

**Step 1: User logs in**
```bash
# Frontend → Identity Service
POST http://localhost:8001/api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

# Returns JWT with tenant_id
```

**Step 2: Frontend creates project**
```bash
# Frontend → Project Service
POST http://localhost:8006/api/v1/projects/
Authorization: Bearer <JWT_TOKEN>
{
  "name": "New Project",
  "client_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "planning",
  "priority": "high"
}

# Project Service extracts tenant_id from JWT
# Creates project with: tenant_id = user's tenant_id
```

**Step 3: Frontend fetches invoices**
```bash
# Frontend → Accounting Service
GET http://localhost:8004/api/v1/invoices/?project_id=<project_uuid>
Authorization: Bearer <JWT_TOKEN>

# Accounting Service extracts tenant_id from JWT
# Returns only invoices from user's tenant
```

**Step 4: Frontend lists tasks**
```bash
# Frontend → Project Service
GET http://localhost:8006/api/v1/tasks/
Authorization: Bearer <JWT_TOKEN>

# Project Service extracts tenant_id from JWT
# Returns only tasks from user's tenant
```

---

## 7. Cross-Service Communication Patterns

### Pattern 1: Direct HTTP Calls

**When to use:**
- Need data from another service
- Simple request/response
- Can use JWT from current request

**Implementation:**
```python
import requests

def call_other_service(service_url, endpoint, token):
    """Generic function to call another service"""
    response = requests.get(
        f"{service_url}{endpoint}",
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json() if response.status_code == 200 else None
```

### Pattern 2: UUID References

**When to use:**
- Storing references to entities in other services
- Denormalizing for performance

**Implementation:**
```python
# Accounting Service stores project_id (UUID)
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project_id = models.UUIDField(db_index=True)  # UUID, not foreign key
    tenant_id = models.UUIDField(db_index=True)
    # ... other fields
```

### Pattern 3: Tenant Filtering

**When to use:**
- Every data query
- Protects data isolation between tenants

**Implementation:**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Always filter by tenant
    tenant_id = self.request.user.tenant_id
    if tenant_id:
        queryset = queryset.filter(tenant_id=tenant_id)
    
    return queryset
```

### Pattern 4: JWT Token Pass-Through

**When to use:**
- Frontend calling multiple services
- Service-to-service calls

**Implementation:**
```python
# Frontend stores JWT in local storage or state
const token = localStorage.getItem('access_token');

// Use for all requests
fetch('http://localhost:8006/api/v1/projects/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

fetch('http://localhost:8004/api/v1/invoices/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 8. Event Bus (Planned, Not Active)

### Current State

**Event bus code exists but not integrated:**
- Location: `toremove/backend/shared/event_bus.py`
- Purpose: Async service communication via RabbitMQ
- Status: Not currently used by services

### Planned Event Flow

**When Event Bus is integrated:**
```
User Created (Identity) → Event Bus → HR Service (create employee record)
User Created (Identity) → Event Bus → Notification Service (send welcome email)
Project Created (Project) → Event Bus → Accounting Service (create invoice)
Task Updated (Project) → Event Bus → Notification Service (send update)
```

### Event Bus Implementation

```python
# In toremove/backend/shared/event_bus.py

class EventBus:
    def publish(self, event_type, payload):
        """Publish event to RabbitMQ"""
        # Send event to RabbitMQ exchange
        pass
    
    def subscribe(self, event_type, handler):
        """Subscribe to events from other services"""
        # Consume events from RabbitMQ
        pass
```

---

## 9. Security Model

### JWT Authentication

**Access Tokens:**
- Last 1 hour
- Contains user_id, tenant_id, role, permissions
- Used for API requests

**Refresh Tokens:**
- Last 7 days
- Used to get new access tokens
- Stored securely (e.g., httpOnly cookie)

### Tenant Isolation

**All users must belong to at least one tenant:**
- UserTenant model links User → Tenant
- JWT includes tenant_id
- All data queries filter by tenant_id
- Users cannot access data from other tenants

### CORS Configuration

**Allow frontend to access services:**
```python
# In each service's settings.py

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend
    "http://localhost:8000",  # Traefik Gateway
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
]

CORS_ALLOW_CREDENTIALS = True
```

---

## 10. Traefik Gateway (Optional)

### When to Use

**Development:** Direct access (ports 8001-8007)
**Production:** Use Traefik gateway (port 8000)

### Traefik Configuration

**API Routes:**
```yaml
# traefik-local.toml

[http.routers]
  [http.routers.identity]
    service = "identity"
    rule = "PathPrefix(`/api/v1/identity`)"

[http.services]
  [http.services.identity]
    loadBalancer = [[url = "http://localhost:8001"]]
```

### Benefits of Using Traefik

- Single entry point for frontend
- No need to manage multiple base URLs
- SSL termination at gateway
- Rate limiting and security policies
- Logging and monitoring

---

## Summary

### Architecture Principles

1. **Service Independence** - Each service is completely self-contained
2. **JWT Authentication** - No database lookups for auth
3. **Tenant-Based Security** - All data filtered by tenant_id
4. **UUID-Only References** - No foreign keys between databases
5. **HTTP Communication** - Services talk via REST APIs with JWT
6. **Stateless Auth** - All user info in JWT token
7. **Scalable** - Easy to add/remove services

### Data Flow

```
Frontend → Identity (login) → JWT Token
    ↓
Frontend → Project Service (with JWT) → Create Project (with tenant_id)
    ↓
Frontend → Accounting Service (with JWT) → Get Invoices (filtered by tenant_id)
    ↓
Frontend → HR Service (with JWT) → Get Leave Data (filtered by tenant_id)
```

### Key Files

| Purpose | Location |
|---------|----------|
| JWT Token Generation | `services/identity-service/identity/jwt_tokens.py` |
| JWT Authentication (other services) | `services/<service>/jwt_auth.py` |
| Shared Auth Module | `services/shared/auth/jwt_auth.py` |
| Service Settings | `services/<service>/<service>_service/settings.py` |

### Benefits

✅ **Performance** - No auth database queries
✅ **Scalability** - Services can be deployed independently
✅ **Security** - Tenant-based data isolation
✅ **Flexibility** - Easy to add new services
✅ **Maintainability** - Clear separation of concerns
✅ **Development** - Teams can work independently on services

---

## Version

**Current:** v1.0 - Complete microservices connection and communication documentation
