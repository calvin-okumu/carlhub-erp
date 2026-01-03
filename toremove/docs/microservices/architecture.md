# DjangoCRM Microservices Architecture

## Overview

DjangoCRM has been migrated from a monolithic Django application to a microservices architecture with 7 independent services, each with its own database. This document provides the architectural overview and service boundaries.

## Architecture Diagram

```
Frontend (Next.js)
        ↓
API Gateway (Traefik)
├── Identity Service (Port 8001) - identity_db
├── Audit Service (Port 8002) - audit_db
├── Notification Service (Port 8003) - stateless
├── Project Service (Port 8004) - project_db
├── Accounting Service (Port 8005) - accounting_db
├── HR Service (Port 8006) - hr_db
└── Sales Service (Port 8007) - sales_db
        ↓
Event Bus (RabbitMQ) + Redis Cache
```

## Service Boundaries

### Identity Service
**Purpose:** User authentication, tenant management, and authorization
**Database:** identity_db (PostgreSQL)
**Models:**
- CustomUser (authentication, profile)
- Tenant (company/organization data)
- UserTenant (user-organization relationships)
- UserProfile (extended user information)
- Department (organizational structure)
- CustomPermission (RBAC permissions)
- PermissionGroup (permission collections)
- Invitation (user onboarding)

**APIs:**
- POST /api/auth/login/ - User login
- POST /api/auth/signup/ - User registration
- POST /api/auth/refresh/ - Token refresh
- GET /api/users/ - User management
- GET /api/tenants/ - Tenant management
- GET /api/users/by-role/ - Users by role (for approvals)

### Audit Service
**Purpose:** Comprehensive audit logging for compliance
**Database:** audit_db (PostgreSQL)
**Models:**
- AuditLog (all system events)

**APIs:**
- GET /api/audit/logs/ - Query audit logs
- POST /api/audit/logs/ - Create audit log (internal)

**Event Consumers:**
- Consumes all audit events from RabbitMQ
- Stores structured audit data

### Notification Service
**Purpose:** Email and notification delivery
**Database:** None (stateless)
**Components:**
- EmailService (SMTP email sending)
- Event consumers for various notification types

**Event Consumers:**
- email.* - Email notifications
- audit.* - Audit-related notifications

### Project Service
**Purpose:** Client and project management
**Database:** project_db (PostgreSQL)
**Models:**
- Client (customer relationships)
- Contract (LPO/contract management)
- Project (project lifecycle)
- Milestone (project phases)
- Sprint (agile iterations)
- Task (individual work items)

**APIs:**
- GET/POST /api/clients/ - Client CRUD
- GET/POST /api/projects/ - Project CRUD
- GET/POST /api/contracts/ - Contract CRUD
- GET/POST /api/milestones/ - Milestone CRUD
- GET/POST /api/sprints/ - Sprint CRUD
- GET/POST /api/tasks/ - Task CRUD

### Accounting Service
**Purpose:** Financial management and billing
**Database:** accounting_db (PostgreSQL)
**Models:**
- Invoice (billing documents)
- Payment (payment records)

**APIs:**
- GET/POST /api/invoices/ - Invoice CRUD
- GET/POST /api/payments/ - Payment CRUD

**Cross-Service Dependencies:**
- Validates client_id with Project Service
- Validates project_id with Project Service
- References user_id from Identity Service

### HR Service
**Purpose:** Leave management and HR operations
**Database:** hr_db (PostgreSQL)
**Models:**
- LeaveRequest (leave applications)
- LeaveBalance (annual leave tracking)
- LeavePolicy (company leave rules)
- LeaveApproval (approval workflow)
- LeaveApprovalWorkflow (configurable workflows)
- LeaveSale (leave buyback)

**APIs:**
- GET/POST /api/leave/requests/ - Leave request CRUD
- GET/POST /api/leave/balances/ - Leave balance management
- GET/POST /api/leave/policies/ - Leave policy management

**Cross-Service Dependencies:**
- Queries user roles from Identity Service
- References user_id from Identity Service

### Sales Service
**Purpose:** Sales pipeline and opportunity management
**Database:** sales_db (PostgreSQL)
**Models:**
- Customer (prospects and leads)
- Opportunity (sales opportunities)
- SalesActivity (interaction tracking)
- SalesTeam (team management)

**APIs:**
- GET/POST /api/sales/customers/ - Customer CRUD
- GET/POST /api/sales/opportunities/ - Opportunity CRUD
- GET/POST /api/sales/activities/ - Activity CRUD
- GET/POST /api/sales/teams/ - Team CRUD

**Cross-Service Dependencies:**
- References user_id from Identity Service
- References tenant_id from Identity Service

## Communication Patterns

### Synchronous (HTTP/REST)
- **Authentication:** All services validate JWT tokens
- **Data Validation:** Cross-service existence checks
- **Real-time Queries:** User details, tenant info
- **Service-to-Service:** RESTful APIs with ServiceClient

### Asynchronous (Event Bus)
- **Audit Logging:** All services emit audit events
- **Notifications:** Email triggers via events
- **Data Synchronization:** Eventual consistency updates
- **Workflow Triggers:** Approval notifications, status changes

## Data Ownership & Consistency

### Database Isolation
Each service owns its data and is the single source of truth for that data. Services communicate via APIs and events rather than direct database access.

### Cross-Service References
Instead of Django foreign keys, services use UUID references:
```python
# Old (monolith)
client = models.ForeignKey(Client, on_delete=models.CASCADE)

# New (microservices)
client_id = models.UUIDField(db_index=True)

@property
def client(self):
    """Lazy load client from project service"""
    response = requests.get(f"{PROJECT_SERVICE_URL}/api/clients/{self.client_id}/")
    return response.json() if response.status_code == 200 else None
```

### Eventual Consistency
- Services maintain their own data copies where needed
- Events propagate changes asynchronously
- Reconciliation jobs handle data drift
- Circuit breakers prevent cascade failures

## Security & Authentication

### JWT Token Flow
1. User logs in via Identity Service
2. Receives JWT access token (24h) and refresh token (7d)
3. All API calls include Authorization: Bearer <token>
4. Services validate tokens independently
5. Token contains user_id, tenant_id, role information

### Service-to-Service Authentication
- Services include X-Service-Auth header
- API Gateway validates service identity
- Internal APIs require service authentication

## Deployment & Scaling

### Independent Scaling
Each service can be scaled independently:
- **Identity Service:** Scale for authentication load
- **Audit Service:** Scale for write-heavy audit logging
- **Project Service:** Scale for project management operations
- **Accounting Service:** Scale for financial operations
- **HR Service:** Scale for leave management
- **Sales Service:** Scale for sales operations
- **Notification Service:** Scale for email processing

### Infrastructure Requirements
- **API Gateway:** Single instance (Traefik)
- **Message Queue:** Clustered RabbitMQ
- **Cache:** Redis cluster
- **Databases:** 6 PostgreSQL instances
- **Monitoring:** Prometheus + Grafana

## Development Workflow

### Local Development
```bash
# Start all infrastructure
make docker-up-microservices

# Services available at:
# - API Gateway: http://localhost:8000
# - Identity: http://localhost:8001
# - Audit: http://localhost:8002
# - Notification: http://localhost:8003
# - Project: http://localhost:8004
# - Accounting: http://localhost:8005
# - HR: http://localhost:8006
# - Sales: http://localhost:8007
```

### Service Development
Each service is a standalone Django application with:
- Independent requirements.txt
- Separate settings.py
- Own database migrations
- Dedicated test suite
- Docker containerization

## Monitoring & Observability

### Key Metrics
- **Service Health:** Response times, error rates, throughput
- **Database Performance:** Query times, connection pools
- **Event Processing:** Message queue depths, processing rates
- **Cross-Service Calls:** Success rates, latency
- **Business Metrics:** User registrations, project creation, etc.

### Logging
- **Structured Logging:** JSON format with correlation IDs
- **Centralized Collection:** ELK stack or similar
- **Log Levels:** ERROR, WARN, INFO, DEBUG
- **Audit Trail:** All user actions logged

## Migration Status

### Completed Services
- ✅ **Identity Service** - User/tenant management
- ✅ **Audit Service** - Event-driven audit logging
- ✅ **Notification Service** - Email delivery
- ✅ **Sales Service** - Sales pipeline
- ✅ **HR Service** - Leave management
- ✅ **Project Service** - Client/project management
- ✅ **Accounting Service** - Financial operations

### Infrastructure
- ✅ **API Gateway** - Traefik routing
- ✅ **Message Queue** - RabbitMQ exchanges
- ✅ **Databases** - 6 PostgreSQL instances
- ✅ **Cache** - Redis integration
- ✅ **Monitoring** - Prometheus/Grafana

### Testing
- ✅ **Unit Tests** - Per service
- ✅ **Integration Tests** - Cross-service workflows
- ✅ **Performance Tests** - Load testing
- ✅ **End-to-End Tests** - Complete user journeys

## Benefits Achieved

### Scalability
- Independent service scaling based on load patterns
- Database optimization per service requirements
- Horizontal scaling without monolithic constraints

### Reliability
- Service isolation prevents cascade failures
- Circuit breakers for resilient inter-service communication
- Event-driven architecture for loose coupling

### Development Velocity
- Independent deployments and rollbacks
- Technology choice flexibility per service
- Smaller codebases easier to maintain

### Operational Excellence
- Comprehensive monitoring and alerting
- Structured logging with correlation IDs
- Automated testing and deployment pipelines

## Future Enhancements

### Phase 2: Advanced Features
- **Distributed Tracing:** Jaeger/Zipkin integration
- **Service Mesh:** Istio for advanced traffic management
- **Event Sourcing:** For audit logs and business events
- **GraphQL Federation:** Unified API layer
- **Multi-Region:** Global deployment strategy

### Phase 3: Optimization
- **Database Sharding:** For high-volume services
- **Read Replicas:** Separate read/write workloads
- **API Versioning:** Backward compatibility management
- **Rate Limiting:** Per-service and per-user limits
- **Advanced Caching:** Multi-level caching strategies

This architecture provides a solid foundation for scalable, maintainable microservices while preserving the rich functionality of the original DjangoCRM monolith.