# Service Layer Quick Reference

## 🚀 Quick Start Guide

This guide helps developers understand and use the new service layer architecture in DjangoCRM.

## 📁 Service Layer Structure

```
accounts/services/
├── __init__.py                 # Service package exports
├── user_profile_service.py      # User profile business logic
├── employee_document_service.py  # Document management logic
└── audit_log_service.py         # Audit operations logic

project/services/
├── __init__.py                 # Service package exports
├── client_service.py            # Client management logic
├── project_service.py           # Project management logic
└── invoice_service.py           # Invoice management logic

leave_management/
├── services.py                  # Leave approval workflow logic
└── (no additional service files)
```

## 🔧 How to Use Services

### 1. Import Services

```python
# Method 1: Import specific service
from accounts.services.user_profile_service import UserProfileService

# Method 2: Import from service package (recommended)
from accounts.services import UserProfileService, EmployeeDocumentService
```

### 2. Common Service Patterns

#### **Get/Create Pattern**
```python
# Get existing resource or create new one
profile = UserProfileService.get_or_create_profile(user=user)

# Always returns a valid profile or raises ValidationError
```

#### **CRUD with Audit Pattern**
```python
# Create with automatic audit logging
document = EmployeeDocumentService.create_document(
    user=user,
    file_data={'file': file, 'file_type': 'pdf'},
    title='Contract',
    request=request  # For IP address and audit context
)

# Update with automatic audit logging
updated_doc = EmployeeDocumentService.update_document(
    user=user,
    document_id=doc_id,
    update_data={'title': 'Updated Contract'},
    request=request
)

# Delete with automatic audit logging
EmployeeDocumentService.delete_document(
    user=user,
    document_id=doc_id,
    request=request
)
```

#### **Permission Checking Pattern**
```python
# Check if user can access resource
if UserProfileService.can_access_profile(current_user, target_user):
    # Proceed with operation
    profile = UserProfileService.get_user_profile(target_user)
else:
    # Return permission denied
    return Response(status=status.HTTP_403_FORBIDDEN)
```

## 🎯 Service Method Examples

### UserProfileService

```python
# Get user profile
profile = UserProfileService.get_user_profile(user=user)

# Create new profile
profile = UserProfileService.create_user_profile(
    user=user,
    job_title='Software Engineer',
    phone='+1234567890',
    street_address='123 Main St',
    city='Tech City',
    country='USA'
)

# Update profile
updated_profile = UserProfileService.update_user_profile(
    user=user,
    profile_data={'job_title': 'Senior Engineer'},
    request=request
)

# Get or create (most common)
profile = UserProfileService.get_or_create_profile(user=user)

# Check permissions
can_access = UserProfileService.can_access_profile(current_user, target_user)
```

### EmployeeDocumentService

```python
# Get all user documents
documents = EmployeeDocumentService.get_user_documents(user=user)

# Get specific document
document = EmployeeDocumentService.get_document(user=user, document_id=123)

# Create document
document = EmployeeDocumentService.create_document(
    user=user,
    file_data={'file': uploaded_file, 'file_type': 'pdf', 'file_size': 1024},
    title='Employment Contract',
    request=request
)

# Update document
updated_doc = EmployeeDocumentService.update_document(
    user=user,
    document_id=123,
    update_data={'title': 'Updated Contract'},
    request=request
)

# Delete document
success = EmployeeDocumentService.delete_document(
    user=user,
    document_id=123,
    request=request
)

# Get document statistics
stats = EmployeeDocumentService.get_document_stats(user=user)
# Returns: {'total_documents': 5, 'total_size': 2048, 'file_types': {'pdf': 3, 'doc': 2}}
```

### AuditLogService

```python
# Get audit logs with filters
logs = AuditLogService.get_audit_logs(
    user=user,
    filters={
        'action': 'profile_updated',
        'date_from': datetime(2023, 1, 1),
        'date_to': datetime(2023, 12, 31)
    }
)

# Search audit logs
search_results = AuditLogService.search_audit_logs(user=user, query='profile')

# Get audit statistics
stats = AuditLogService.get_audit_log_statistics(user=user, days=30)
# Returns: {'total_logs': 150, 'action_distribution': {...}, ...}

# Export audit logs
csv_data = AuditLogService.export_audit_logs(
    user=user,
    format_type='csv',
    filters={'action': 'profile_updated'}
)

# Cleanup old logs
deleted_count = AuditLogService.cleanup_old_logs(days=365)
```

## 🔄 Migrating from Views to Services

### Before (Old Pattern)
```python
class UserProfileView(generics.RetrieveUpdateAPIView):
    def perform_update(self, serializer):
        # Manual audit logging
        old_data = {
            'job_title': serializer.instance.job_title,
            'phone': serializer.instance.phone,
            # ... more fields
        }

        super().perform_update(serializer)

        new_data = {
            'job_title': serializer.instance.job_title,
            'phone': serializer.instance.phone,
            # ... more fields
        }

        # Manual tenant context
        tenant = None
        try:
            user_tenant = self.request.user.usertenants.filter(is_approved=True).first()
            if user_tenant:
                tenant = user_tenant.tenant
        except:
            pass

        # Manual audit logging
        AuditLogger.log_event(
            action='user_profile_update',
            resource_type='user_profile',
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(self.request)
        )
```

### After (Service Pattern)
```python
class UserProfileView(generics.RetrieveUpdateAPIView):
    def get_object(self):
        # Service handles profile creation logic
        return UserProfileService.get_or_create_profile(self.request.user)

    def perform_update(self, serializer):
        # Service handles all business logic and audit logging
        UserProfileService.update_user_profile(
            user=self.request.user,
            profile_data=serializer.validated_data,
            request=self.request
        )
        # No need to call super().perform_update()
```

## 🧪 Testing Services

### Unit Test Example
```python
class TestUserProfileService(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.tenant = TenantFactory()
        UserTenantFactory(user=self.user, tenant=self.tenant, is_approved=True)

    def test_create_profile_with_audit(self):
        # Create profile through service
        profile = UserProfileService.create_user_profile(
            user=self.user,
            job_title='Software Engineer'
        )

        # Verify profile was created
        self.assertEqual(profile.job_title, 'Software Engineer')

        # Verify audit log was created automatically
        audit_log = AuditLog.objects.filter(
            action='profile_created',
            user=self.user
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.new_values['job_title'], 'Software Engineer')
```

### Integration Test Example
```python
class TestUserProfileAPI(APITestCase):
    def test_profile_update_uses_service(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        # Make API request
        response = self.client.put('/api/accounts/profile/', {
            'job_title': 'Product Manager'
        })

        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify service was called (audit log exists)
        audit_log = AuditLog.objects.filter(
            action='profile_updated',
            user=user
        ).first()
        self.assertIsNotNone(audit_log)
```

## 📋 Best Practices

### ✅ Do's
- **Use services for all business logic**
- **Include request parameter for audit context**
- **Handle ValidationError exceptions from services**
- **Use permission checking methods before operations**
- **Test services independently of views**

### ❌ Don'ts
- **Don't access models directly from views**
- **Don't implement business logic in views**
- **Don't forget audit logging (services handle this)**
- **Don't skip permission checks**

## 🔍 Debugging Service Issues

### Common Problems

#### **Import Errors**
```python
# ❌ Wrong
from .services.user_profile_service import UserProfileService

# ✅ Correct
from accounts.services.user_profile_service import UserProfileService
# or
from accounts.services import UserProfileService
```

#### **Missing Request Context**
```python
# ❌ Missing request (no IP address in audit)
UserProfileService.update_user_profile(user, data, None)

# ✅ Include request for full audit context
UserProfileService.update_user_profile(user, data, request)
```

#### **Permission Issues**
```python
# ❌ Not checking permissions
profile = UserProfileService.get_user_profile(target_user)

# ✅ Check permissions first
if UserProfileService.can_access_profile(current_user, target_user):
    profile = UserProfileService.get_user_profile(target_user)
else:
    return Response(status=status.HTTP_403_FORBIDDEN)
```

## 📚 Additional Resources

- **[Service Layer Documentation](docs/SERVICE_LAYER.md)** - Complete architecture guide
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Full API reference
- **[Development Guidelines](AGENTS.md)** - Build/test commands and workflows

## 🆘 Getting Help

If you encounter issues with the service layer:

1. **Check service method signatures** - All parameters are typed
2. **Look at existing examples** - Check other views using services
3. **Run tests** - Services have comprehensive test coverage
4. **Check audit logs** - Services automatically log operations

The service layer is designed to make development easier and more maintainable. If it feels complicated, you might be overthinking it!
