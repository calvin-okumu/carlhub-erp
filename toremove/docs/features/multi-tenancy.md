# Multi-Tenancy

DjangoCRM implements complete multi-tenant architecture to ensure data isolation and security across different organizations.

## Tenant Architecture

### Database-Level Isolation

Each tenant has isolated data through:
- **Row-Level Security**: Automatic tenant filtering on all queries
- **Tenant Context**: All operations include tenant identification
- **Data Segregation**: No cross-tenant data access

### URL-Based Tenancy

Tenants can be accessed via:
- **Subdomains**: `tenant1.example.com`, `tenant2.example.com`
- **URL Prefixes**: `example.com/tenant1/`, `example.com/tenant2/`
- **Custom Domains**: `tenant1-custom-domain.com`

## Tenant Management

### Creating Tenants

```bash
curl -X POST http://localhost:8000/api/tenants/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": "acme.example.com",
    "is_active": true
  }'
```

### Tenant Configuration

```json
{
  "id": "tenant-uuid",
  "name": "Acme Corporation",
  "domain": "acme.example.com",
  "schema_name": "tenant_acme",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

## User-Tenant Relationships

### User Registration

Users can belong to multiple tenants with different roles:

```json
{
  "user": "user-uuid",
  "tenant": "tenant-uuid",
  "role": "manager",
  "is_owner": false,
  "permissions": ["project.create", "client.read"]
}
```

### Role-Based Access

Default roles:
- **Owner**: Full administrative access
- **Manager**: Project and client management
- **Employee**: Task execution and updates
- **Client**: Limited project visibility

## Data Isolation

### Automatic Filtering

All database queries automatically include tenant context:

```python
# Automatically filtered by tenant
projects = Project.objects.all()  # Only returns tenant's projects

# Manual tenant specification (admin only)
projects = Project.objects.filter(tenant=tenant_id)
```

### Security Measures

- **Tenant Context Middleware**: Enforces tenant isolation on every request
- **Permission Classes**: Role-based access control
- **Audit Logging**: Track all tenant-related operations
- **Data Encryption**: Sensitive data encrypted per tenant

## Tenant Switching

### For Multi-Tenant Users

Users with access to multiple tenants can switch contexts:

```bash
# Get user's tenants
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/members/

# Switch tenant context (via frontend)
# Frontend handles tenant selection and token refresh
```

## Tenant Administration

### Tenant Owners

Tenant owners can:
- **Manage Users**: Invite, assign roles, remove users
- **Configure Settings**: Tenant-specific configuration
- **View Analytics**: Tenant-wide reporting
- **Manage Billing**: Subscription and payment management

### System Administrators

System admins can:
- **Create Tenants**: Set up new tenant organizations
- **Manage Subscriptions**: Handle billing and plan management
- **System Monitoring**: Global system health
- **Data Management**: Backup and restore operations

## Subscription Management

### Plan-Based Access

Different subscription tiers:
- **Free**: Limited users and projects
- **Professional**: Standard features, unlimited projects
- **Enterprise**: Advanced features, custom integrations

### Usage Tracking

Monitor tenant usage:
- **User Count**: Active users per tenant
- **Storage Usage**: Data and file storage
- **API Calls**: Rate limiting and usage tracking
- **Feature Usage**: Advanced feature utilization

## Migration and Upgrades

### Tenant Data Migration

When upgrading plans or migrating data, use Django's built-in data management:

```bash
# Export tenant data (filter by tenant in your application logic)
python manage.py dumpdata --natural-foreign --natural-primary -o tenant_data.json

# Import tenant data
python manage.py loaddata tenant_data.json
```

### Schema Updates

Database schema changes are applied per tenant:

```python
# Standard Django migrations apply to all tenants
python manage.py migrate
```

## Best Practices

### Tenant Setup
1. **Clear Naming**: Descriptive tenant names and domains
2. **Role Assignment**: Proper role distribution from start
3. **Data Structure**: Plan data organization early
4. **User Training**: Educate users on multi-tenant concepts

### Ongoing Management
1. **Regular Audits**: Review user access and permissions
2. **Usage Monitoring**: Track resource utilization
3. **Performance Optimization**: Monitor tenant-specific performance
4. **Backup Strategy**: Regular tenant data backups

### Security
1. **Access Reviews**: Regular permission audits
2. **Data Encryption**: Ensure sensitive data is encrypted
3. **Audit Logging**: Maintain comprehensive activity logs
4. **Incident Response**: Tenant-specific security incident handling

## Troubleshooting

### Common Issues

**Cross-tenant data access**
- Verify middleware is active
- Check permission classes
- Review query filtering

**Tenant switching problems**
- Validate user-tenant relationships
- Check token validity
- Verify frontend tenant selection

**Performance issues**
- Monitor tenant-specific queries
- Optimize database indexes
- Implement caching strategies

**Permission errors**
- Review role assignments
- Check permission inheritance
- Validate user-tenant links</content>
</xai:function_call">

Assistant: Now create crm-core.md in applications.

<xai:function_call name="write">
<parameter name="filePath">docs/applications/crm-core.md
