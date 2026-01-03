# Service Layer Architecture Documentation

## 📋 Overview

DjangoCRM implements a **3-layer architecture** with a dedicated service layer that abstracts business logic from views and models. This architecture provides better separation of concerns, improved testability, and enhanced code maintainability.

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Views     │  │  Serializers│  │ Permissions │  │
│  │   (HTTP)    │  │  (Data)    │  │  (Access)   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │UserProfile  │  │EmployeeDoc  │  │  AuditLog   │  │
│  │  Service    │  │  Service    │  │  Service    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Client    │  │   Project   │  │   Invoice   │  │
│  │  Service    │  │  Service    │  │  Service    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Models    │  │  Managers   │  │  Database   │  │
│  │ (ORM)      │  │ (Queries)   │  │ (PostgreSQL)│  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Service Layer Benefits

### 1. **Separation of Concerns**
- **Views**: Handle HTTP requests/responses, authentication, serialization
- **Services**: Contain business logic, validation, audit logging
- **Models**: Define data structure, persistence, relationships

### 2. **Code Reusability**
```python
# Same service can be used in multiple contexts
from accounts.services import UserProfileService

# In API views
UserProfileService.update_user_profile(user, data, request)

# In management commands
UserProfileService.update_user_profile(user, data, None)

# In background tasks
UserProfileService.update_user_profile(user, data, None)
```

### 3. **Enhanced Testability**
```python
# Services can be unit tested independently
class TestUserProfileService(TestCase):
    def test_update_profile(self):
        user = UserFactory()
        profile = UserProfileService.update_user_profile(
            user=user,
            profile_data={'job_title': 'Engineer'},
            request=None
        )
        self.assertEqual(profile.job_title, 'Engineer')
```

### 4. **Consistent Audit Logging**
All operations through services automatically generate audit logs with proper context.

## 📁 Service Classes

### Accounts App Services

#### **UserProfileService**
**Location**: `accounts/services/user_profile_service.py`

**Responsibilities**:
- User profile CRUD operations
- Profile validation and business rules
- Automatic audit logging
- Permission checking

**Key Methods**:
```python
@staticmethod
def get_user_profile(user: User) -> Optional[UserProfile]

@staticmethod
def create_user_profile(user: User, **profile_data) -> UserProfile

@staticmethod
def update_user_profile(user: User, profile_data: Dict[str, Any], request=None) -> UserProfile

@staticmethod
def get_or_create_profile(user: User) -> UserProfile

@staticmethod
def can_access_profile(user: User, target_user: User) -> bool
```

**Usage Example**:
```python
# In views.py
class UserProfileView(generics.RetrieveUpdateAPIView):
    def perform_update(self, serializer):
        UserProfileService.update_user_profile(
            user=self.request.user,
            profile_data=serializer.validated_data,
            request=self.request
        )
```

#### **EmployeeDocumentService**
**Location**: `accounts/services/employee_document_service.py`

**Responsibilities**:
- Document CRUD operations
- File validation and processing
- Document access control
- Automatic audit logging

**Key Methods**:
```python
@staticmethod
def get_user_documents(user: User) -> List[EmployeeDocument]

@staticmethod
def create_document(user: User, file_data: Dict[str, Any], title: str, request=None) -> EmployeeDocument

@staticmethod
def update_document(user: User, document_id: int, update_data: Dict[str, Any], request=None) -> EmployeeDocument

@staticmethod
def delete_document(user: User, document_id: int, request=None) -> bool

@staticmethod
def get_document_stats(user: User) -> Dict[str, Any]
```

#### **AuditLogService**
**Location**: `accounts/services/audit_log_service.py`

**Responsibilities**:
- Audit log querying and filtering
- Permission-based access control
- Audit data export
- Audit statistics and analytics

**Key Methods**:
```python
@staticmethod
def get_audit_logs(user: User, filters: Optional[Dict[str, Any]] = None) -> List[AuditLog]

@staticmethod
def search_audit_logs(user: User, query: str) -> List[AuditLog]

@staticmethod
def get_audit_log_statistics(user: User, days: int = 30) -> Dict[str, Any]

@staticmethod
def export_audit_logs(user: User, format_type: str = 'csv', filters: Optional[Dict[str, Any]] = None) -> str

@staticmethod
def cleanup_old_logs(days: int = 365) -> int
```

### Project App Services

#### **ClientService**
**Location**: `project/services/client_service.py`

**Responsibilities**:
- Client management operations
- Client validation and business rules
- Client-project relationship management

#### **ProjectService**
**Location**: `project/services/project_service.py`

**Responsibilities**:
- Project lifecycle management
- Progress calculation and aggregation
- Project-team relationship management

#### **InvoiceService**
**Location**: `project/services/invoice_service.py`

**Responsibilities**:
- Invoice and payment processing
- Financial calculations
- Billing workflow management

### Leave Management App Services

#### **LeaveApprovalWorkflowService**
**Location**: `leave_management/services.py`

**Responsibilities**:
- Multi-level leave approval workflow management
- Approval chain determination and execution
- Workflow status tracking and progression
- Automatic approver resolution based on roles
- Leave balance updates upon approval

**Key Methods**:
```python
@classmethod
def get_approval_chain(leave_request) -> List[Tuple[str, User]]

@classmethod
def process_approval(leave_request, approver, action, notes="", request=None) -> Dict[str, Any]

@classmethod
def get_workflow_status(leave_request) -> Dict[str, Any]

@classmethod
def _get_workflow_approvers(leave_request, workflow) -> List[Tuple[str, User]]

@classmethod
def _resolve_level_approvers(level, leave_request) -> List[User]
```

**Usage Example**:
```python
# In views.py
class LeaveRequestViewSet(viewsets.ModelViewSet):
    def perform_approval(self, request, leave_request, action):
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request=leave_request,
            approver=request.user,
            action=action,
            notes=request.data.get('notes', ''),
            request=request
        )
        return result
```

## 🔄 Request Flow

### Typical API Request Flow

```
1. HTTP Request → View Layer
   ├── Authentication check
   ├── Permission validation
   └── Request data serialization

2. View Layer → Service Layer
   ├── Business logic execution
   ├── Data validation
   ├── Permission checks
   └── Audit logging

3. Service Layer → Model Layer
   ├── Database operations
   ├── Data persistence
   └── Relationship management

4. Response Flow (Reverse)
   ├── Model → Service (data processing)
   ├── Service → View (business result)
   └── View → HTTP Response (serialized data)
```

### Example: User Profile Update

```python
# 1. View receives PUT /api/accounts/profile/
class UserProfileView(generics.RetrieveUpdateAPIView):
    def perform_update(self, serializer):
        # 2. View delegates to service
        UserProfileService.update_user_profile(
            user=self.request.user,
            profile_data=serializer.validated_data,
            request=self.request
        )

# 3. Service handles business logic
class UserProfileService:
    @staticmethod
    def update_user_profile(user, profile_data, request):
        # Get existing profile
        profile = UserProfileService.get_user_profile(user)

        # Store old values for audit
        old_data = {...}

        # Update profile
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()

        # Get new values for audit
        new_data = {...}

        # Log audit event
        AuditLogger.log_event(
            action='profile_updated',
            resource_type='user_profile',
            tenant=tenant,
            user=user,
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(request)
        )

        return profile
```

## 🧪 Testing Services

### Unit Testing Services

```python
class TestUserProfileService(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.tenant = TenantFactory()
        UserTenantFactory(user=self.user, tenant=self.tenant, is_approved=True)

    def test_create_user_profile(self):
        profile = UserProfileService.create_user_profile(
            user=self.user,
            job_title='Software Engineer',
            phone='+1234567890'
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.job_title, 'Software Engineer')
        self.assertEqual(profile.phone, '+1234567890')

    def test_update_user_profile_with_audit(self):
        # Create initial profile
        profile = UserProfileService.create_user_profile(user=self.user)

        # Update profile
        updated_profile = UserProfileService.update_user_profile(
            user=self.user,
            profile_data={'job_title': 'Senior Engineer'},
            request=None
        )

        # Verify update
        self.assertEqual(updated_profile.job_title, 'Senior Engineer')

        # Verify audit log was created
        audit_log = AuditLog.objects.filter(
            action='profile_updated',
            user=self.user
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.old_values['job_title'], None)
        self.assertEqual(audit_log.new_values['job_title'], 'Senior Engineer')
```

### Integration Testing with Views

```python
class TestUserProfileAPI(APITestCase):
    def test_profile_update_through_service(self):
        user = UserFactory()
        tenant = TenantFactory()
        UserTenantFactory(user=user, tenant=tenant, is_approved=True)

        self.client.force_authenticate(user=user)

        data = {'job_title': 'Product Manager'}
        response = self.client.put('/api/accounts/profile/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['job_title'], 'Product Manager')

        # Verify service was called and audit log created
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.job_title, 'Product Manager')

        audit_log = AuditLog.objects.filter(
            action='profile_updated',
            user=user
        ).first()
        self.assertIsNotNone(audit_log)
```

## 🔧 Best Practices

### 1. **Service Method Design**
- Use `@staticmethod` for stateless operations
- Return model instances, not dictionaries
- Include comprehensive type hints
- Handle validation and business rules

### 2. **Error Handling**
```python
@staticmethod
def update_user_profile(user, profile_data, request):
    try:
        profile = UserProfileService.get_user_profile(user)
        if not profile:
            raise ValidationError("User profile does not exist")

        # Business logic...
        return profile

    except ValidationError as e:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise ValidationError("Failed to update profile")
```

### 3. **Audit Logging**
```python
# Always include audit context
AuditLogger.log_event(
    action='action_name',
    resource_type='resource_type',
    tenant=tenant,  # Get from user context
    user=user,
    resource_id=str(resource.id),
    old_values=old_data,
    new_values=new_data,
    ip_address=get_client_ip(request)
)
```

### 4. **Permission Checking**
```python
@staticmethod
def can_access_resource(user, resource):
    # Users can access their own resources
    if resource.user == user:
        return True

    # Superusers can access any resource
    if user.is_superuser:
        return True

    # Check tenant membership
    return UserProfileService._same_tenant(user, resource.user)
```

## 📈 Performance Considerations

### 1. **Query Optimization**
```python
# Use select_related/prefetch_related in services
def get_user_with_profile(user_id):
    return User.objects.select_related('profile').get(id=user_id)

def get_user_documents_with_stats(user):
    return (
        EmployeeDocument.objects
        .filter(user=user)
        .prefetch_related('audit_logs')
        .annotate(
            total_size=Sum('file_size'),
            document_count=Count('id')
        )
    )
```

### 2. **Caching Strategy**
```python
from django.core.cache import cache

@staticmethod
def get_user_profile_cached(user):
    cache_key = f'user_profile_{user.id}'
    profile = cache.get(cache_key)

    if not profile:
        profile = UserProfileService.get_user_profile(user)
        cache.set(cache_key, profile, timeout=300)  # 5 minutes

    return profile
```

### 3. **Enhanced Caching with Backend Compatibility**
```python
# Cache backend capability checks implemented
from saasCRM.enhanced_caching import CacheManager

# Automatic backend detection and fallback
CacheManager.delete_pattern("*user*")  # Works with Redis, LocMemCache, etc.
CacheManager.invalidate_model('project', tenant_id)  # Graceful degradation
```

### 4. **Request Correlation for Performance Monitoring**
```python
# Automatic correlation ID tracking
from saasCRM.correlation_middleware import get_correlation_id

# In services - automatic correlation tracking
def process_user_data(user, request):
    correlation_id = get_correlation_id(request)
    logger.info(f"[{correlation_id}] Processing user {user.id}")

# All log entries now include correlation IDs for tracing
# Format: [env] [correlation_id] LEVEL timestamp module message
```

## 🚀 Future Enhancements

### 1. **Async Services**
```python
# Future: Async service operations
class AsyncUserProfileService:
    @staticmethod
    async def update_user_profile_async(user, profile_data, request):
        # Async database operations
        profile = await UserProfile.objects.aget(user=user)
        # ... async processing
        return profile
```

### 2. **Event-Driven Architecture**
```python
# Future: Event-driven service updates
@receiver(profile_updated)
def handle_profile_update(sender, **kwargs):
    # Send notifications, update caches, etc.
    pass
```

### 3. **Service Composition**
```python
# Future: Complex service operations
class UserOnboardingService:
    @staticmethod
    def onboard_new_user(user, tenant_data, profile_data):
        # Compose multiple services
        tenant = TenantService.create_tenant(**tenant_data)
        UserProfileService.create_user_profile(user, **profile_data)
        NotificationService.send_welcome_email(user)
        return tenant
```

## 📚 Additional Resources

- [Django Service Layer Pattern](https://django-best-practices.readthedocs.io/en/latest/applications.html#service-layer)
- [Domain-Driven Design in Django](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Testing Django Applications](https://docs.djangoproject.com/en/stable/topics/testing/)

This service layer architecture provides a solid foundation for building maintainable, testable, and scalable Django applications.
