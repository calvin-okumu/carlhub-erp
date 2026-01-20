# Audit Logging

DjangoCRM provides comprehensive audit logging capabilities to track all user actions and system events for security, compliance, and troubleshooting purposes.

## Overview

The audit logging system automatically captures and stores detailed information about user activities, system events, and security-related actions across the entire application.

## Features

### 🔍 Comprehensive Event Tracking
- **User Actions**: Login, logout, profile updates, password changes
- **Resource Changes**: Creation, updates, and deletion of projects, tasks, clients
- **Security Events**: Failed login attempts, permission changes, token misuse
- **Administrative Actions**: User approvals, role assignments, tenant management

### 📊 Detailed Event Information
Each audit log entry contains:
- **Timestamp**: Exact time of the event
- **User**: Who performed the action
- **Action**: Type of action performed
- **Resource**: What was affected
- **Changes**: Before/after values for updates
- **Context**: IP address, user agent, tenant information

### 🔐 Access Control
- **Tenant Isolation**: Users can only view audit logs for their tenant
- **Role-Based Access**: Only tenant admins and owners can access audit logs
- **Superuser Access**: Superusers can view all audit logs across tenants

## Accessing Audit Logs

### Django Admin Interface
Audit logs are available in the Django admin at `/admin/accounts/auditlog/` with:
- **List View**: Timestamp, action, resource type, user, tenant, IP address
- **Filtering**: By action, resource type, tenant, user, date range
- **Search**: By user email, resource ID, IP address
- **Read-only**: All fields are read-only for security

### REST API
Access audit logs programmatically via `/api/accounts/audit-logs/`:

```bash
# Get all audit logs (paginated)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/accounts/audit-logs/

# Filter by action
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/accounts/audit-logs/?action=user_login"

# Filter by user
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/accounts/audit-logs/?user=user-uuid"

# Sort by timestamp (newest first)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/accounts/audit-logs/?ordering=-timestamp"
```

### API Response Format
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/accounts/audit-logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "action": "user_login",
      "resource_type": "user",
      "resource_id": "user-uuid",
      "old_values": null,
      "new_values": null,
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-01-15T10:30:00Z",
      "metadata": null,
      "user_email": "john.doe@example.com",
      "tenant_name": "Acme Corp"
    }
  ]
}
```

## Event Types

### User Lifecycle Events
- **`user_signup`**: New user registration
- **`user_login`**: Successful user login
- **`user_logout`**: User logout
- **`user_profile_update`**: Profile information changes
- **`user_password_change`**: Password modifications

### Invitation & Membership Events
- **`invitation_sent`**: Team member invitation sent
- **`invitation_used`**: Invitation accepted by user
- **`invitation_cancelled`**: Invitation cancelled
- **`member_approved`**: Team member approved by admin

### Resource Management Events
- **`project_created`**: New project creation
- **`task_created`**: New task creation
- **`client_created`**: New client creation
- **`milestone_created`**: New milestone creation

### Security Events
- **`security_failed_login`**: Failed login attempt
- **`security_token_misuse`**: Invalid token usage
- **`admin_user_suspended`**: User account suspension
- **`admin_user_activated`**: User account activation

## Data Structure

### AuditLog Model Fields
- **`tenant`**: Associated tenant (for multi-tenant isolation)
- **`user`**: User who performed the action
- **`action`**: Action type (from predefined choices)
- **`resource_type`**: Type of resource affected
- **`resource_id`**: Identifier of the affected resource
- **`old_values`**: Previous state (JSON format)
- **`new_values`**: New state (JSON format)
- **`ip_address`**: Client IP address
- **`user_agent`**: Browser/client user agent string
- **`timestamp`**: Event timestamp (auto-generated)
- **`metadata`**: Additional context data (JSON format)

### Change Tracking Example
```json
{
  "action": "user_profile_update",
  "resource_type": "user_profile",
  "old_values": {
    "first_name": "John",
    "phone": "+1-555-0123"
  },
  "new_values": {
    "first_name": "Johnny",
    "phone": "+1-555-0987"
  },
  "metadata": {
    "updated_fields": ["first_name", "phone"]
  }
}
```

## Use Cases

### 🔍 Security Monitoring
- Track failed login attempts and suspicious activity
- Monitor administrative actions and permission changes
- Audit user access patterns and unusual behavior

### 📋 Compliance & Auditing
- Maintain detailed records for regulatory compliance
- Track changes to sensitive data and configurations
- Provide audit trails for financial and legal requirements

### 🐛 Troubleshooting
- Debug user-reported issues with activity history
- Track system changes and their impact
- Identify patterns in user behavior and system usage

### 📊 Analytics & Reporting
- Generate reports on user activity and engagement
- Analyze system usage patterns and peak times
- Track feature adoption and user workflows

## Configuration

### Automatic Logging
Audit logging is automatically enabled for:
- User authentication events
- Profile and password changes
- Resource creation, updates, and deletion
- Administrative actions
- Security-related events

### Custom Logging
Add custom audit events in your code:

```python
from accounts.audit import AuditLogger

# Log a custom event
AuditLogger.log_event(
    action='custom_action',
    resource_type='custom_resource',
    user=request.user,
    resource_id=str(resource.id),
    old_values=old_data,
    new_values=new_data,
    ip_address=get_client_ip(request),
    metadata={'custom_info': 'additional context'}
)
```

## Performance Considerations

### Database Storage
- Audit logs are stored in the database with proper indexing
- Automatic cleanup policies can be implemented for old logs
- Consider archiving old logs to separate storage for long-term retention

### Query Optimization
- Indexed fields: tenant, user, action, resource_type, resource_id, timestamp
- Use filtering and pagination to manage large result sets
- Consider read replicas for heavy audit log querying

### Retention Policies
- Implement log rotation based on your compliance requirements
- Archive old logs to cost-effective storage
- Define retention periods based on regulatory requirements

## Security Best Practices

### Access Control
- Audit logs are read-only to prevent tampering
- Access is restricted to tenant administrators
- Superuser access is logged separately

### Data Protection
- Sensitive information is not logged in audit entries
- IP addresses and user agents are tracked for security analysis
- Logs are encrypted at rest and in transit

### Monitoring
- Monitor audit log access patterns
- Alert on unusual audit log activity
- Regular review of audit log integrity

## Integration

### Third-Party Tools
- Export audit logs to SIEM systems
- Integrate with log aggregation platforms
- Connect to compliance monitoring tools

### API Integration
- Use webhooks for real-time audit event notifications
- Integrate with external security monitoring systems
- Build custom dashboards and reporting tools

## Troubleshooting

### Common Issues

**No Audit Logs Appearing**
- Check user permissions (must be tenant admin or superuser)
- Verify tenant association for the user
- Check that the action is properly logged in the codebase

**Performance Issues**
- Use pagination for large result sets
- Apply filters to reduce query scope
- Consider database optimization for large audit log tables

**Missing Events**
- Ensure `AuditLogger.log_event()` is called in relevant views
- Check that middleware is properly configured
- Verify that the event type is defined in ACTION_CHOICES

### Log Analysis Tools
```bash
# Count events by action type
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/accounts/audit-logs/" | jq '.results | group_by(.action) | map({action: .[0].action, count: length})'

# Find recent security events
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/accounts/audit-logs/?action__startswith=security&ordering=-timestamp"
```</content>
</xai:function_call"> 

Assistant: Now I need to update the features README to include the audit logging feature. Let me add it to the table of contents and core features. 

<xai:function_call name="edit">
<parameter name="filePath">docs/features/README.md