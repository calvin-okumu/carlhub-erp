# Client Management

Clients represent the organizations or individuals that commission work in DjangoCRM. Each project belongs to a client, and the system supports comprehensive client relationship management.

## Client Lifecycle

### Client Creation

Clients can be created through the API or admin interface:

```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "email": "contact@acme.com",
    "phone": "+1-555-0123",
    "status": "prospect"
  }'
```

### Client Statuses

- **Prospect**: Potential client, initial contact
- **Active**: Current client with active projects
- **Inactive**: Former client, no active projects
- **Archived**: Historical client record

## Client CRUD Operations

### List Clients

```bash
# Get all clients
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/clients/

# Filter by status
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/clients/?status=active"
```

### Get Client Details

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/clients/client-slug/
```

### Update Client

```bash
curl -X PUT http://localhost:8000/api/clients/client-slug/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active", "phone": "+1-555-0124"}'
```

### Delete Client

```bash
curl -X DELETE http://localhost:8000/api/clients/client-slug/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Client Relationships

### Projects

Each client can have multiple projects:

```json
{
  "name": "Acme Corporation",
  "projects_count": 3,
  "projects": [
    {
      "name": "Website Redesign",
      "status": "active",
      "budget": "50000.00"
    }
  ]
}
```

### Invoices

Clients can have associated invoices for billing:

```json
{
  "client": "acme-corporation",
  "invoices": [
    {
      "amount": "15000.00",
      "paid": true,
      "issued_at": "2025-01-15"
    }
  ]
}
```

## Client Information

### Contact Details

- **Name**: Full client organization name
- **Email**: Primary contact email
- **Phone**: Contact phone number
- **Status**: Current relationship status

### Automatic Features

- **Slug Generation**: URL-friendly identifier
- **Project Counting**: Automatic count of associated projects
- **Validation**: Phone number format validation

## Client Templates

For common client types:

- **Enterprise**: Large organizations with complex requirements
- **SMB**: Small to medium businesses
- **Startup**: New companies with agile development needs
- **Individual**: Personal projects and consulting

## Client Reporting

Clients provide valuable business intelligence:

- **Project Portfolio**: Overview of all client projects
- **Financial Summary**: Total value and payment status
- **Activity Timeline**: Historical project engagement
- **Satisfaction Metrics**: Project completion and feedback

## Best Practices

### Client Onboarding

1. **Complete Information**: Gather all contact details
2. **Status Setting**: Set appropriate initial status
3. **Communication**: Establish preferred contact methods
4. **Requirements Gathering**: Understand business needs

### Ongoing Management

1. **Regular Updates**: Keep contact information current
2. **Project Tracking**: Monitor project progress and budgets
3. **Communication**: Maintain regular client communication
4. **Feedback Collection**: Gather project feedback and satisfaction

### Client Retention

1. **Relationship Building**: Develop strong client relationships
2. **Value Demonstration**: Show project value and ROI
3. **Proactive Communication**: Anticipate needs and issues
4. **Quality Assurance**: Ensure high-quality deliverables</content>
</xai:function_call">  
</xai:function_call name="write">
<parameter name="filePath">docs/features/user-management.md