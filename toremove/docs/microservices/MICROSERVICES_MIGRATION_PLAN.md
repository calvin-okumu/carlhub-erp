# DjangoCRM Microservices Migration Plan

## Executive Summary

This document outlines a comprehensive **12-week plan** to migrate DjangoCRM from a monolithic Django application to a microservices architecture with separate databases per service. The migration will transform the current single Django application with 5 apps into 7 independent microservices while maintaining full API compatibility for the frontend.

### Key Objectives
- **Independent Scaling**: Each service can scale independently based on load
- **Technology Flexibility**: Different services can use different technologies
- **Fault Isolation**: Service failures don't bring down the entire system
- **Team Autonomy**: Different teams can work on different services
- **Maintainability**: Smaller, focused services are easier to maintain
- **Event-Driven Architecture**: Reliable inter-service communication with comprehensive error handling

### Migration Scope
- **Backend Only**: Frontend remains unchanged (API Gateway maintains compatibility)
- **Zero Downtime**: Parallel running during transition
- **Data Strategy**: Fresh databases (no data migration needed)
- **Timeline**: **12 weeks** with buffer time (extended from 10 weeks for robustness)
- **Rollback**: Ability to revert to monolith quickly
- **Event Bus**: Production-ready messaging system with all critical fixes

### Critical Improvements Added
- **Extended Timeline**: 10 → 12 weeks with buffer for unexpected issues
- **Event Bus Hardening**: Complete implementation with thread safety, retry logic, DLQ, async publishing
- **Communication Strategy**: Cached metadata pattern, circuit breakers, API composition
- **Transaction Management**: Saga patterns for distributed transactions
- **Monitoring Stack**: Prometheus + Grafana + Jaeger + ELK for full observability
- **API Gateway**: Complete Traefik configuration with routing and middleware
- **Testing Expansion**: Contract testing, chaos engineering, data consistency validation
- **Revised Order**: Identity+Audit together, Notification POC early for pipeline validation

---

## Current Architecture

### Monolithic Structure
```
Frontend (Next.js)
        ↓
Django Monolith (Single Process)
├── accounts (users, tenants, permissions)
├── project (clients, projects, tasks)
├── accounting (invoices, payments)
├── leave_management (leave requests, approvals)
└── sales (customers, opportunities)
        ↓
Single PostgreSQL Database
```

### Current Apps & Models

**accounts app** (725 lines):
- CustomUser, UserProfile, Tenant, UserTenant
- CustomPermission, PermissionGroup, Department
- Invitation, AuditLog

**project app** (740 lines):
- Client, Contract, Project, Milestone, Sprint, Task

**accounting app** (272 lines):
- Invoice, Payment

**leave_management app** (840 lines):
- LeaveRequest, LeaveBalance, LeavePolicy
- LeaveApproval, LeaveApprovalWorkflow, LeaveSale

**sales app** (460 lines):
- Customer, Opportunity, SalesActivity, SalesTeam

---

## Target Architecture

### Microservices Structure
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

### Service Boundaries

| Service | Responsibility | Database | Port | Models |
|---------|----------------|----------|------|--------|
| **Identity Service** | User authentication, tenant management, permissions | identity_db | 8001 | CustomUser, Tenant, UserTenant, UserProfile, Department, CustomPermission, PermissionGroup, Invitation |
| **Audit Service** | System audit logging | audit_db | 8002 | AuditLog |
| **Notification Service** | Email/SMS notifications | None (stateless) | 8003 | - |
| **Project Service** | Client and project management | project_db | 8004 | Client, Contract, Project, Milestone, Sprint, Task |
| **Accounting Service** | Financial management | accounting_db | 8005 | Invoice, Payment |
| **HR Service** | Leave management | hr_db | 8006 | LeaveRequest, LeaveBalance, LeavePolicy, LeaveApproval, LeaveApprovalWorkflow, LeaveSale |
| **Sales Service** | Sales pipeline | sales_db | 8007 | Customer, Opportunity, SalesActivity, SalesTeam |

---

## Infrastructure Requirements

### Development Environment
- **CPU**: 8 cores minimum (all services running)
- **RAM**: 16GB minimum (6 databases + 7 services + infrastructure)
- **Storage**: 100GB minimum (databases + Docker images)
- **Docker**: Version 20.10+ with Docker Compose
- **Python**: 3.11+ for all services

### Production Environment (Initial)
- **CPU**: 17 cores total across all services
- **RAM**: 11GB total
- **Storage**: 500GB minimum
- **Monthly Cost**: $300-500 (AWS/GCP/Azure)

### Infrastructure Components

#### Databases (6 PostgreSQL instances)
```yaml
# docker-compose.microservices.yml
services:
  postgres-identity:
    image: postgres:15
    environment:
      POSTGRES_DB: identity_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["identity_data:/var/lib/postgresql/data"]
    ports: ["5432:5432"]

  postgres-audit:
    image: postgres:15
    environment:
      POSTGRES_DB: audit_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["audit_data:/var/lib/postgresql/data"]
    ports: ["5433:5432"]

  postgres-project:
    image: postgres:15
    environment:
      POSTGRES_DB: project_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["project_data:/var/lib/postgresql/data"]
    ports: ["5434:5432"]

  postgres-accounting:
    image: postgres:15
    environment:
      POSTGRES_DB: accounting_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["accounting_data:/var/lib/postgresql/data"]
    ports: ["5435:5432"]

  postgres-hr:
    image: postgres:15
    environment:
      POSTGRES_DB: hr_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["hr_data:/var/lib/postgresql/data"]
    ports: ["5436:5432"]

  postgres-sales:
    image: postgres:15
    environment:
      POSTGRES_DB: sales_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes: ["sales_data:/var/lib/postgresql/data"]
    ports: ["5437:5432"]
```

#### Message Queue (RabbitMQ)
```yaml
rabbitmq:
  image: rabbitmq:3.12-management
  ports:
    - "5672:5672"   # AMQP
    - "15672:15672" # Management UI
  environment:
    RABBITMQ_DEFAULT_USER: admin
    RABBITMQ_DEFAULT_PASS: password
  volumes: ["rabbitmq_data:/var/lib/rabbitmq"]
```

#### Cache (Redis)
```yaml
redis:
  image: redis:alpine
  ports: ["6379:6379"]
  volumes: ["redis_data:/data"]
  command: redis-server --appendonly yes
```

#### API Gateway (Traefik)
```yaml
api-gateway:
  image: traefik:v3.0
  ports:
    - "8000:80"     # API Gateway
    - "8080:8080"   # Dashboard
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  command:
    - --api.insecure=true
    - --providers.docker=true
    - --providers.docker.exposedbydefault=false
```

---

## 12-Week Migration Timeline

### **Phase 1: Foundation & Critical Infrastructure (Weeks 1-2)**

#### **Week 1: Core Infrastructure & Event Bus Hardening**

**Day 1-2: Infrastructure Setup**
- [ ] Set up 6 PostgreSQL databases (one per service)
- [ ] Configure RabbitMQ with exchanges and queues
- [ ] Set up Redis cache with clustering
- [ ] Deploy API Gateway (Traefik) with routing rules
- [ ] Configure monitoring stack (Prometheus + Grafana + Jaeger)
- [ ] Set up ELK stack for centralized logging
- [ ] Create Docker Compose configuration
- [ ] Test all infrastructure components

**Day 3-4: Event Bus Implementation & Critical Fixes**
- [ ] **Fix Critical Event Bus Issues**:
  - ✅ Add `import uuid` to event_bus.py
  - ✅ Implement `EventConsumer` class with subscribe/consume methods
  - ✅ Add thread safety with `threading.Lock()`
  - ✅ Add retry logic with exponential backoff
  - ✅ Configure Dead Letter Queue (DLQ) for failed messages
  - ✅ Add `publish_async()` method to prevent blocking

- [ ] **Fix Important Event Bus Issues**:
  - ✅ Add graceful shutdown handler
  - ✅ Add event validation (Pydantic schemas)
  - ✅ Add correlation ID tracking
  - ✅ Add circuit breaker pattern
  - ✅ Add metrics/monitoring integration

- [ ] **Test Event Bus Thoroughly**:
  - ✅ Publish/consume test events
  - ✅ Thread safety validation under concurrent load
  - ✅ Failure scenario testing (network issues, RabbitMQ restart)
  - ✅ Performance benchmarking (1000+ events/second)
  - ✅ Dead letter queue validation

**Day 5-7: Communication Strategy & Authentication**
- [ ] **Implement Service-to-Service Communication Patterns**:
  - **Cached Metadata Pattern**: Store frequently accessed data locally
  - **API Composition**: Gateway-level data aggregation
  - **Circuit Breaker Pattern**: Resilience for synchronous calls
- [ ] **Complete Authentication Flow**:
  - JWT token generation/validation per service
  - Service-to-service authentication headers
  - Token refresh mechanism
  - Permission propagation strategy

#### **Week 2: Monitoring, Testing & Validation**

**Day 8-10: Enhanced Monitoring & Observability**
- [ ] **Distributed Tracing Setup** (Jaeger):
  - Service mesh integration
  - Request correlation IDs
  - Performance bottleneck identification
- [ ] **Metrics Collection** (Prometheus):
  - Service health metrics (response times, error rates, throughput)
  - Database connection pools and query performance
  - Event processing rates and queue depths
  - Business metrics (user registrations, invoice creation)
- [ ] **Centralized Logging** (ELK):
  - Structured JSON logging with correlation IDs
  - Log aggregation from all services
  - Alerting rules for critical failures
- [ ] **Event Bus Monitoring**:
  - Message publish/consume rates
  - Dead letter queue monitoring
  - Circuit breaker status tracking

**Day 11-12: Testing Framework & Event Bus Integration**
- [ ] **Contract Testing Setup** (Pact):
  - API contract validation between services
  - Consumer-driven contract testing
- [ ] **Event Bus Integration Testing**:
  - Cross-service event flow validation
  - Identity service publishes → Audit service consumes
  - Notification service consumes from all services
  - Event correlation and tracing validation
- [ ] **Chaos Engineering**:
  - Service failure simulation
  - Network latency injection
  - Database connection failures
  - Event bus disruption testing
- [ ] **Data Consistency Validation**:
  - Cross-service referential integrity checks
  - Eventual consistency monitoring and alerting

**Day 13-14: Documentation & Planning**
- [ ] Update all documentation with new sections
- [ ] Create runbooks for operational procedures
- [ ] Define RTO/RPO for each service
- [ ] Finalize migration order and rollback plans
- [ ] Create troubleshooting guides

### **Phase 2: Identity + Audit Services (Weeks 3-4)**

#### **Week 3: Identity Service (Core Authentication)**

**Why First:** All other services depend on user/tenant authentication

#### Day 1-3: Service Structure
Create `backend/services/identity-service/`:
```
identity-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── identity_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── tenant.py
│   │   ├── user_tenant.py
│   │   ├── permission.py
│   │   └── department.py
│   ├── serializers/
│   ├── views/
│   │   ├── auth_views.py
│   │   ├── user_views.py
│   │   ├── tenant_views.py
│   │   └── permission_views.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── tenant_service.py
│   │   └── permission_service.py
│   ├── consumers/
│   │   └── __init__.py
│   └── middleware.py
└── tests/
```

#### Day 4-7: Authentication API
**auth_views.py**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from ..models import CustomUser, UserTenant
from ..serializers import UserSerializer, TenantSerializer
from shared.event_bus import event_bus

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get user's tenant context
        user_tenant = UserTenant.objects.filter(
            user=user, is_approved=True
        ).first()

        if not user_tenant:
            return Response({'error': 'No approved tenant'}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        from shared.jwt_utils import generate_access_token, generate_refresh_token

        access_token = generate_access_token({
            'user_id': str(user.id),
            'tenant_id': str(user_tenant.tenant.id),
            'role': user_tenant.role,
            'email': user.email,
        })

        refresh_token = generate_refresh_token({'user_id': str(user.id)})

        # Emit login event
        event_bus.publish(
            exchange='identity',
            routing_key='user.login',
            event_data={
                'user_id': str(user.id),
                'tenant_id': str(user_tenant.tenant.id),
                'timestamp': timezone.now().isoformat(),
            }
        )

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSerializer(user).data,
            'tenant': TenantSerializer(user_tenant.tenant).data,
        })

class SignupView(APIView):
    def post(self, request):
        # Create tenant
        tenant = Tenant.objects.create(
            name=request.data['company_name'],
            domain=request.data.get('domain', ''),
            industry=request.data.get('industry', ''),
            company_size=request.data.get('company_size', '1-10'),
        )

        # Create user
        user = CustomUser.objects.create_user(
            email=request.data['email'],
            password=request.data['password'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
        )

        # Create user-tenant relationship
        UserTenant.objects.create(
            user=user,
            tenant=tenant,
            is_owner=True,
            role='Tenant Owner',
            is_approved=True,
        )

        # Emit signup event
        event_bus.publish(
            exchange='identity',
            routing_key='user.signup',
            event_data={
                'user_id': str(user.id),
                'tenant_id': str(tenant.id),
                'email': user.email,
            }
        )

        return Response({
            'user': UserSerializer(user).data,
            'tenant': TenantSerializer(tenant).data,
        }, status=status.HTTP_201_CREATED)
```

#### Day 8-10: Database Setup & Testing
- [ ] Create identity_db migrations
- [ ] Set up Docker configuration
- [ ] Test authentication endpoints
- [ ] Test event publishing
- [ ] Create unit tests

### **Week 4-5: Audit Service**

**Why Second:** Isolated data, needs identity service dependency only

#### Day 1-3: Service Structure
Create `backend/services/audit-service/`:
```
audit-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── audit_service/
│   ├── models/
│   │   └── audit_log.py
│   ├── serializers/
│   ├── views/
│   ├── services/
│   │   └── audit_service.py
│   ├── consumers/
│   │   └── audit_consumer.py
│   └── middleware.py
└── tests/
```

#### Day 4-7: Event Consumer
**audit_consumer.py**:
```python
import pika
import json
import logging
from ..models import AuditLog
from shared.service_client import ServiceClient

logger = logging.getLogger(__name__)

class AuditEventConsumer:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.identity_client = ServiceClient(
            os.getenv('IDENTITY_SERVICE_URL', 'http://localhost:8001')
        )

    def start_consuming(self):
        connection = pika.BlockingConnection(
            pika.URLParameters(self.rabbitmq_url)
        )
        channel = connection.channel()

        # Declare exchange and queue
        channel.exchange_declare('audit', 'topic', durable=True)
        channel.queue_declare('audit.logs', durable=True)
        channel.queue_bind('audit.logs', 'audit', routing_key='audit.*')

        def callback(ch, method, properties, body):
            try:
                event_data = json.loads(body)
                self.process_audit_event(event_data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing audit event: {e}")
                # Requeue for retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume('audit.logs', on_message_callback=callback)
        logger.info("Audit consumer started")
        channel.start_consuming()

    def process_audit_event(self, event_data):
        data = event_data.get('data', {})

        # Validate user exists (optional, for data integrity)
        if data.get('user_id'):
            try:
                self.identity_client.get(f"/api/users/{data['user_id']}/")
            except:
                logger.warning(f"User {data['user_id']} not found in identity service")

        # Create audit log
        AuditLog.objects.create(
            tenant_id=data.get('tenant_id'),
            user_id=data.get('user_id'),
            action=data['action'],
            resource_type=data['resource_type'],
            resource_id=data.get('resource_id'),
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            timestamp=data.get('timestamp'),
        )

        logger.info(f"Audit log created: {data['action']} on {data['resource_type']}")
```

#### Day 8-10: Database Setup & Testing
- [ ] Create audit_db migrations
- [ ] Set up Docker configuration
- [ ] Test event consumption
- [ ] Test audit log creation
- [ ] Create integration tests

### **Week 5-6: Notification Service (Stateless)**

**Why Third:** No database, easy to extract, decouples email sending

#### Day 1-5: Service Structure
Create `backend/services/notification-service/`:
```
notification-service/
├── Dockerfile
├── requirements.txt
├── notification_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── consumers/
│   │   ├── email_consumer.py
│   │   ├── audit_consumer.py
│   │   └── notification_consumer.py
│   ├── templates/
│   │   └── emails/
│   │       ├── invitation.html
│   │       ├── leave_approval.html
│   │       └── password_reset.html
│   └── services/
│       └── email_service.py
└── tests/
```

#### Day 6-10: Event Consumers & Email Service
**email_consumer.py**:
```python
import pika
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)

class EmailEventConsumer:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.email_service = EmailService()

    def start_consuming(self):
        connection = pika.BlockingConnection(
            pika.URLParameters(self.rabbitmq_url)
        )
        channel = connection.channel()

        # Declare exchange and queue
        channel.exchange_declare('notification', 'topic', durable=True)
        channel.queue_declare('email.notifications', durable=True)
        channel.queue_bind('email.notifications', 'notification', routing_key='email.*')

        def callback(ch, method, properties, body):
            try:
                event_data = json.loads(body)
                self.process_email_event(event_data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing email event: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume('email.notifications', on_message_callback=callback)
        logger.info("Email consumer started")
        channel.start_consuming()

    def process_email_event(self, event_data):
        data = event_data.get('data', {})
        email_type = data.get('type')
        recipient = data.get('recipient')
        context = data.get('context', {})

        if email_type == 'invitation':
            self.email_service.send_invitation_email(recipient, context)
        elif email_type == 'leave_approval':
            self.email_service.send_leave_approval_email(recipient, context)
        elif email_type == 'password_reset':
            self.email_service.send_password_reset_email(recipient, context)
        elif email_type == 'user_signup':
            self.email_service.send_welcome_email(recipient, context)
        else:
            logger.warning(f"Unknown email type: {email_type}")
```

**Email Service**:
```python
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template import Template, Context
from django.conf import settings

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@django-crm.com')

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email

        # Attach parts
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())

    def send_invitation_email(self, email: str, context: dict):
        """Send tenant invitation email"""
        subject = f"You're invited to join {context['tenant_name']}"

        html_template = self._load_template('invitation.html')
        html_content = self._render_template(html_template, context)

        self.send_email(email, subject, html_content)

    def send_leave_approval_email(self, email: str, context: dict):
        """Send leave approval notification"""
        subject = f"Leave Request {context['status']}"

        html_template = self._load_template('leave_approval.html')
        html_content = self._render_template(html_template, context)

        self.send_email(email, subject, html_content)

    def send_welcome_email(self, email: str, context: dict):
        """Send welcome email to new users"""
        subject = f"Welcome to {context['tenant_name']}"

        html_template = self._load_template('welcome.html')
        html_content = self._render_template(html_template, context)

        self.send_email(email, subject, html_content)

    def _load_template(self, template_name: str) -> str:
        """Load email template"""
        template_path = os.path.join(
            os.path.dirname(__file__), '..', 'templates', 'emails', template_name
        )
        with open(template_path, 'r') as f:
            return f.read()

    def _render_template(self, template: str, context: dict) -> str:
        """Render template with context"""
        django_template = Template(template)
        django_context = Context(context)
        return django_template.render(django_context)
```

### **Week 6-7: Sales Service**

**Why Fourth:** Lowest complexity, minimal cross-app dependencies

#### Day 1-3: Service Structure
Create `backend/services/sales-service/`:
```
sales-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── sales_service/
│   ├── models/
│   │   ├── customer.py
│   │   ├── opportunity.py
│   │   ├── sales_activity.py
│   │   └── sales_team.py
│   ├── serializers/
│   ├── views/
│   ├── services/
│   └── consumers/
└── tests/
```

#### Day 4-7: Handle User/Tenant References
**models/customer.py**:
```python
from django.db import models
from shared.service_client import ServiceClient
import os

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = models.SlugField(max_length=255, unique=True)

    # UUID references (no FK)
    tenant_id = models.UUIDField(db_index=True)
    assigned_to_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_by_id = models.UUIDField(null=True, blank=True)

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, default='prospect')
    lead_score = models.IntegerField(default=0)
    # ... other fields

    class Meta:
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['assigned_to_id', 'status']),
        ]

    @property
    def assigned_to(self):
        """Get assigned user from identity service"""
        if not self.assigned_to_id:
            return None

        identity_client = ServiceClient(
            os.getenv('IDENTITY_SERVICE_URL', 'http://localhost:8001')
        )

        try:
            return identity_client.get(f"/api/users/{self.assigned_to_id}/")
        except:
            return None

    @property
    def created_by(self):
        """Get creator from identity service"""
        if not self.created_by_id:
            return None

        identity_client = ServiceClient(
            os.getenv('IDENTITY_SERVICE_URL', 'http://localhost:8001')
        )

        try:
            return identity_client.get(f"/api/users/{self.created_by_id}/")
        except:
            return None

    def save(self, *args, **kwargs):
        # Emit events
        from shared.event_bus import event_bus
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            event_bus.publish(
                exchange='sales',
                routing_key='customer.created',
                event_data={
                    'customer_id': str(self.id),
                    'tenant_id': str(self.tenant_id),
                    'name': self.name,
                    'email': self.email,
                }
            )
```

#### Day 8-10: Database Setup & Testing
- [ ] Create sales_db migrations
- [ ] Set up Docker configuration
- [ ] Test cross-service user lookups
- [ ] Test event publishing
- [ ] Create integration tests

### **Week 7-8: HR Service (Leave Management)**

**Why Fifth:** Medium complexity, but depends on user roles from identity service

#### Day 1-3: Service Structure
Create `backend/services/hr-service/`:
```
hr-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── hr_service/
│   ├── models/
│   │   ├── leave_request.py
│   │   ├── leave_balance.py
│   │   ├── leave_policy.py
│   │   ├── leave_approval.py
│   │   ├── leave_approval_workflow.py
│   │   └── leave_sale.py
│   ├── serializers/
│   ├── views/
│   ├── services/
│   │   └── approval_service.py
│   └── consumers/
└── tests/
```

#### Day 4-7: Handle User Role Queries
**services/approval_service.py**:
```python
from shared.service_client import ServiceClient
import os

class LeaveApprovalService:
    def __init__(self):
        self.identity_client = ServiceClient(
            os.getenv('IDENTITY_SERVICE_URL', 'http://localhost:8001')
        )

    def get_approvers_for_workflow(self, tenant_id: str, workflow):
        """Get approvers from identity service based on roles"""
        approvers = []

        for level in workflow.approval_levels:
            role = level['role']  # 'department_manager', 'hr_manager', etc.

            # Query identity service for users with this role
            try:
                users = self.identity_client.get(
                    f"/api/users/by-role/",
                    params={
                        'tenant_id': tenant_id,
                        'role': role,
                        'department_id': level.get('department_id'),
                    }
                )

                approvers.extend(users)
            except Exception as e:
                logger.error(f"Failed to get approvers for role {role}: {e}")

        return approvers

    def create_approval_steps(self, leave_request):
        """Create approval steps for leave request"""
        from ..models import LeaveApproval
        from shared.event_bus import event_bus

        policy = leave_request.get_policy()
        workflow = policy.approval_workflow
        approvers = self.get_approvers_for_workflow(
            str(leave_request.tenant_id), workflow
        )

        for i, approver in enumerate(approvers, 1):
            LeaveApproval.objects.create(
                leave_request=leave_request,
                approver_id=approver['id'],  # UUID reference
                approval_level=approver['role'],
                order=i,
            )

        # Emit approval workflow created event
        event_bus.publish(
            exchange='hr',
            routing_key='leave.approval_workflow.created',
            event_data={
                'leave_request_id': str(leave_request.id),
                'tenant_id': str(leave_request.tenant_id),
                'employee_id': str(leave_request.employee_id),
                'approval_levels': len(approvers),
            }
        )
```

#### Day 8-10: Database Setup & Testing
- [ ] Create hr_db migrations
- [ ] Set up Docker configuration
- [ ] Test approval workflow
- [ ] Test cross-service user queries
- [ ] Create integration tests

### **Week 8-9: Project Service**

**Why Sixth:** Core service, referenced by accounting service

#### Day 1-3: Service Structure
Create `backend/services/project-service/`:
```
project-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── project_service/
│   ├── models/
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── project.py
│   │   ├── milestone.py
│   │   ├── sprint.py
│   │   └── task.py
│   ├── serializers/
│   ├── views/
│   ├── services/
│   │   ├── project_service.py
│   │   ├── client_service.py
│   │   └── progress_service.py
│   └── consumers/
└── tests/
```

#### Day 4-7: Handle Multi-Service Relationships
**models/client.py**:
```python
from django.db import models
from shared.service_client import ServiceClient
from shared.event_bus import event_bus
import os

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = models.SlugField(max_length=255, unique=True)

    # UUID references
    tenant_id = models.UUIDField(db_index=True)
    primary_contact_id = models.UUIDField(null=True, blank=True, db_index=True)
    account_manager_id = models.UUIDField(null=True, blank=True, db_index=True)

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, default='prospect')
    # ... other fields

    @property
    def primary_contact(self):
        """Get primary contact from identity service"""
        if not self.primary_contact_id:
            return None

        identity_client = ServiceClient(
            os.getenv('IDENTITY_SERVICE_URL', 'http://localhost:8001')
        )

        try:
            return identity_client.get(f"/api/users/{self.primary_contact_id}/")
        except:
            return None

    def save(self, *args, **kwargs):
        # Emit event on client creation/update
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            event_bus.publish(
                exchange='project',
                routing_key='client.created',
                event_data={
                    'client_id': str(self.id),
                    'tenant_id': str(self.tenant_id),
                    'name': self.name,
                    'email': self.email,
                }
            )
```

#### Day 8-10: Database Setup & Testing
- [ ] Create project_db migrations
- [ ] Set up Docker configuration
- [ ] Test progress calculations
- [ ] Test event publishing
- [ ] Create integration tests

### **Week 9-10: Accounting Service & Integration**

**Why Last:** Most complex, references both users and project.Client/Project

#### Day 1-3: Service Structure
Create `backend/services/accounting-service/`:
```
accounting-service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── accounting_service/
│   ├── models/
│   │   ├── invoice.py
│   │   └── payment.py
│   ├── serializers/
│   ├── views/
│   ├── services/
│   │   ├── invoice_service.py
│   │   └── payment_service.py
│   └── consumers/
└── tests/
```

#### Day 4-7: Handle Cross-Service References
**models/invoice.py**:
```python
from django.db import models
from shared.service_client import ServiceClient
from shared.event_bus import event_bus
import os

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = models.SlugField(max_length=255, unique=True)

    # UUID references
    tenant_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(db_index=True)  # References project.Client
    project_id = models.UUIDField(null=True, blank=True, db_index=True)  # References project.Project
    created_by_id = models.UUIDField(null=True, blank=True)

    # Financial details
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='draft')

    def clean(self):
        """Validate client and project exist"""
        if self.client_id:
            project_client = ServiceClient(
                os.getenv('PROJECT_SERVICE_URL', 'http://localhost:8004')
            )
            try:
                project_client.get(f"/api/clients/{self.client_id}/")
            except:
                raise ValidationError("Client does not exist")

        if self.project_id:
            project_client = ServiceClient(
                os.getenv('PROJECT_SERVICE_URL', 'http://localhost:8004')
            )
            try:
                project_client.get(f"/api/projects/{self.project_id}/")
            except:
                raise ValidationError("Project does not exist")

    @property
    def client(self):
        """Get client from project service"""
        if not self.client_id:
            return None

        project_client = ServiceClient(
            os.getenv('PROJECT_SERVICE_URL', 'http://localhost:8004')
        )

        try:
            return project_client.get(f"/api/clients/{self.client_id}/")
        except:
            return None

    @property
    def project(self):
        """Get project from project service"""
        if not self.project_id:
            return None

        project_client = ServiceClient(
            os.getenv('PROJECT_SERVICE_URL', 'http://localhost:8004')
        )

        try:
            return project_client.get(f"/api/projects/{self.project_id}/")
        except:
            return None

    def save(self, *args, **kwargs):
        # Emit events
        from shared.event_bus import event_bus
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            event_bus.publish(
                exchange='accounting',
                routing_key='invoice.created',
                event_data={
                    'invoice_id': str(self.id),
                    'tenant_id': str(self.tenant_id),
                    'client_id': str(self.client_id),
                    'amount': str(self.amount),
                    'currency': self.currency,
                }
            )
```

#### Day 8-10: End-to-End Testing & Cutover
- [ ] Test complete workflows across all services
- [ ] Performance testing
- [ ] API Gateway configuration
- [ ] Documentation updates
- [ ] Deployment preparation

---

## 🔧 Critical Technical Details (Added)

### **Service-to-Service Communication Strategy**

#### **1. Cached Metadata Pattern (Primary)**
```python
# In Accounting Service - Cache client data locally
class Invoice(models.Model):
    client_id = models.UUIDField()  # FK to project.Client

    # Cached data (updated via events)
    _client_name = models.CharField(max_length=255, blank=True)
    _client_email = models.EmailField(blank=True)

    @property
    def client(self):
        """Get client data from cache or API"""
        if self._client_name:
            return {
                'id': self.client_id,
                'name': self._client_name,
                'email': self._client_email,
            }

        # Fallback to API call with circuit breaker
        try:
            return project_service.get_client(self.client_id)
        except ServiceUnavailableError:
            return {'id': self.client_id, 'name': 'Unknown', 'email': ''}
```

#### **2. API Composition at Gateway**
```yaml
# Traefik configuration for data aggregation
http:
  routers:
    invoice-detail:
      rule: "Path(`/api/invoices/{id}`)"
      service: invoice-composition-service

  services:
    invoice-composition-service:
      loadBalancer:
        servers:
          - url: "http://api-gateway:8080"  # Internal composition endpoint
```

#### **3. Circuit Breaker Implementation**
```python
# Global circuit breakers per service
identity_breaker = CircuitBreaker('identity-service', failure_threshold=5, timeout=60)
project_breaker = CircuitBreaker('project-service', failure_threshold=3, timeout=30)

@identity_breaker.call
def get_user(user_id):
    return identity_client.get(f"/api/users/{user_id}")

@project_breaker.call
def get_client(client_id):
    return project_client.get(f"/api/clients/{client_id}")
```

### **Distributed Transaction Management**

#### **Saga Pattern for Invoice Creation**
```python
class InvoiceSaga:
    def __init__(self, invoice_data):
        self.invoice_data = invoice_data
        self.steps = []

    def execute(self):
        try:
            # Step 1: Validate client exists
            client = self.validate_client()
            self.steps.append('client_validated')

            # Step 2: Validate project exists (if provided)
            if self.invoice_data.get('project_id'):
                project = self.validate_project()
                self.steps.append('project_validated')

            # Step 3: Create invoice
            invoice = self.create_invoice()
            self.steps.append('invoice_created')

            # Step 4: Publish events
            self.publish_events(invoice)
            self.steps.append('events_published')

            return invoice

        except Exception as e:
            # Compensate completed steps
            self.compensate()
            raise e

    def compensate(self):
        """Rollback completed steps in reverse order"""
        for step in reversed(self.steps):
            if step == 'events_published':
                # No compensation needed for events
                pass
            elif step == 'invoice_created':
                # Delete created invoice
                self.delete_invoice()
            # Add other compensations...
```

### **API Gateway Configuration (Complete)**

```yaml
# docker-compose.microservices.yml - Complete Traefik config
services:
  api-gateway:
    image: traefik:v3.0
    ports:
      - "8000:80"      # API Gateway
      - "8080:8080"    # Dashboard
      - "8443:443"     # HTTPS (future)
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic:/etc/traefik/dynamic:ro
    command:
      - --configFile=/etc/traefik/traefik.yml
    networks:
      - backend
    depends_on:
      - identity-service
      - audit-service
      - project-service
      - accounting-service
      - hr-service
      - sales-service
```

```yaml
# traefik/dynamic/routing.yml
http:
  routers:
    # Identity Service
    identity-login:
      rule: "Path(`/api/auth/login`) || Path(`/api/auth/signup`) || Path(`/api/auth/refresh`)"
      service: identity-service
      middlewares: ["auth-rate-limit", "cors"]

    identity-users:
      rule: "PathPrefix(`/api/users`)"
      service: identity-service
      middlewares: ["jwt-auth", "cors"]

    identity-tenants:
      rule: "PathPrefix(`/api/tenants`)"
      service: identity-service
      middlewares: ["jwt-auth", "cors"]

    # Audit Service
    audit-logs:
      rule: "PathPrefix(`/api/audit`)"
      service: audit-service
      middlewares: ["jwt-auth", "audit-rate-limit", "cors"]

    # Project Service
    project-clients:
      rule: "PathPrefix(`/api/clients`)"
      service: project-service
      middlewares: ["jwt-auth", "cors"]

    project-projects:
      rule: "PathPrefix(`/api/projects`)"
      service: project-service
      middlewares: ["jwt-auth", "cors"]

    # Accounting Service
    accounting-invoices:
      rule: "PathPrefix(`/api/invoices`)"
      service: accounting-service
      middlewares: ["jwt-auth", "cors"]

    accounting-payments:
      rule: "PathPrefix(`/api/payments`)"
      service: accounting-service
      middlewares: ["jwt-auth", "cors"]

    # HR Service
    hr-leaves:
      rule: "PathPrefix(`/api/leave`)"
      service: hr-service
      middlewares: ["jwt-auth", "cors"]

    # Sales Service
    sales-customers:
      rule: "PathPrefix(`/api/sales/customers`)"
      service: sales-service
      middlewares: ["jwt-auth", "cors"]

    sales-opportunities:
      rule: "PathPrefix(`/api/sales/opportunities`)"
      service: sales-service
      middlewares: ["jwt-auth", "cors"]

  services:
    identity-service:
      loadBalancer:
        servers:
          - url: "http://identity-service:8001"
        healthCheck:
          path: "/health/"
          interval: "30s"
          timeout: "5s"

    audit-service:
      loadBalancer:
        servers:
          - url: "http://audit-service:8002"
        healthCheck:
          path: "/health/"
          interval: "30s"
          timeout: "5s"

    # ... similar for other services

  middlewares:
    jwt-auth:
      jwt:
        signingSecret: "{{ env `JWT_SECRET_KEY` }}"
        tokenQueryKey: "token"
        claims: "exp,user_id,tenant_id"
        forwardAuth:
          address: "http://identity-service:8001/api/auth/validate"

    auth-rate-limit:
      rateLimit:
        burst: 10
        average: 5

    cors:
      cors:
        allowOrigins: ["http://localhost:3000", "https://yourdomain.com"]
        allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allowHeaders: ["Authorization", "Content-Type", "X-Requested-With"]
        maxAge: 86400
```

### **Monitoring & Observability Setup**

#### **Prometheus Configuration**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'identity-service'
    static_configs:
      - targets: ['identity-service:8001']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'audit-service'
    static_configs:
      - targets: ['audit-service:8002']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'project-service'
    static_configs:
      - targets: ['project-service:8004']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'accounting-service'
    static_configs:
      - targets: ['accounting-service:8005']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'hr-service'
    static_configs:
      - targets: ['hr-service:8006']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8007']
    metrics_path: '/metrics/'
    scrape_interval: 5s

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']
    metrics_path: '/metrics'
```

#### **Grafana Dashboards**
- **Service Health Dashboard**: Response times, error rates, throughput
- **Database Performance**: Connection pools, query times, slow queries
- **Event Processing**: Message queue depths, processing rates, failures
- **Business Metrics**: User registrations, invoice creation, project completion
- **Infrastructure**: CPU, memory, disk usage across all services

#### **Distributed Tracing (Jaeger)**
```yaml
# monitoring/jaeger-config.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Accept jaeger.thrift over HTTP
    environment:
      COLLECTOR_OTLP_ENABLED: true
    networks:
      - backend
```

### **Error Handling & Resilience Patterns**

#### **Retry Policies**
```python
# shared/retry.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def call_external_service(service_func, *args, **kwargs):
    return service_func(*args, **kwargs)
```

#### **Timeout Configuration**
```python
# Service-specific timeouts
SERVICE_TIMEOUTS = {
    'identity-service': 2,      # Fast auth checks
    'project-service': 5,       # Complex queries
    'accounting-service': 10,   # Financial operations
    'audit-service': 3,         # Logging operations
}
```

#### **Fallback Mechanisms**
```python
def get_user_with_fallback(user_id):
    """Get user with multiple fallback strategies"""
    try:
        # Primary: Direct API call
        return identity_client.get(f"/api/users/{user_id}")
    except ServiceUnavailableError:
        try:
            # Secondary: Cached data
            return cache.get(f"user:{user_id}")
        except CacheMiss:
            # Tertiary: Return minimal data
            return {
                'id': user_id,
                'name': 'Unknown User',
                'email': f'user-{user_id}@unknown.com'
            }
```

## Cross-Service Communication Strategy

### Synchronous Communication (HTTP/REST)

**Use Cases:**
- Authentication/authorization queries
- Real-time validation (does this user exist?)
- API calls that need immediate response

**Implementation:**
- Service-to-service calls via `ServiceClient`
- Circuit breaker pattern for resilience
- Timeout handling (5 seconds default)

### Asynchronous Communication (Event Bus)

**Use Cases:**
- Audit logging (no immediate response needed)
- Email notifications (fire and forget)
- Cross-service data updates
- Progress updates (eventual consistency)

**Event Schema:**
```python
# Event structure
{
    "event_id": "uuid",
    "event_type": "routing.key",
    "timestamp": "ISO 8601",
    "data": {
        # Event-specific data
    }
}

# Key Events
EVENTS = {
    # Identity Service
    'user.created': {'user_id': str, 'tenant_id': str, 'email': str},
    'user.login': {'user_id': str, 'tenant_id': str},
    'user.signup': {'user_id': str, 'tenant_id': str, 'email': str},

    # Project Service
    'client.created': {'client_id': str, 'tenant_id': str, 'name': str},
    'project.created': {'project_id': str, 'tenant_id': str, 'client_id': str},
    'task.completed': {'task_id': str, 'project_id': str, 'tenant_id': str},

    # Accounting Service
    'invoice.created': {'invoice_id': str, 'tenant_id': str, 'client_id': str, 'amount': str},
    'invoice.paid': {'invoice_id': str, 'tenant_id': str, 'amount': str},

    # HR Service
    'leave.approved': {'leave_request_id': str, 'tenant_id': str, 'employee_id': str},
    'leave.submitted': {'leave_request_id': str, 'tenant_id': str, 'employee_id': str},

    # Sales Service
    'customer.created': {'customer_id': str, 'tenant_id': str, 'name': str},
    'opportunity.won': {'opportunity_id': str, 'tenant_id': str, 'value': str},

    # Notification Service (consumes all)
    'email.invitation': {'recipient': str, 'tenant_name': str, 'token': str},
    'email.leave_approval': {'recipient': str, 'status': str, 'leave_type': str},
}
```

### Circuit Breaker Pattern

```python
# shared/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, service_name: str, failure_threshold: int = 5, timeout: int = 60):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, func):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {self.service_name}")

        try:
            result = func()
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = 'open'

            raise e

# Usage
identity_breaker = CircuitBreaker('identity-service')

@identity_breaker.call
def get_user(user_id):
    return identity_client.get(f"/api/users/{user_id}/")
```

---

## Testing Strategy

### Unit Testing (Per Service)

**Example: Identity Service**
```python
# identity_service/tests/test_auth.py
class AuthenticationTests(TestCase):
    def test_signup_creates_user_and_tenant(self):
        response = self.client.post('/api/auth/signup/', data={
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'company_name': 'Test Company',
        })

        self.assertEqual(response.status_code, 201)

        # Verify user created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

        # Verify tenant created
        self.assertTrue(Tenant.objects.filter(name='Test Company').exists())

        # Verify user-tenant relationship
        user = User.objects.get(email='test@example.com')
        self.assertTrue(UserTenant.objects.filter(user=user).exists())

    def test_login_returns_jwt_tokens(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

        response = self.client.post('/api/auth/login/', data={
            'email': 'test@example.com',
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

        # Verify tokens are valid
        access_token = response.data['access_token']
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(decoded['email'], 'test@example.com')
```

### Integration Testing (Cross-Service)

**Example: Complete User Journey**
```python
# tests/integration/test_full_workflow.py
class FullWorkflowIntegrationTest(TestCase):
    def test_complete_user_journey(self):
        """Test complete user journey across all services"""

        # 1. Sign up (Identity Service)
        signup_response = requests.post(
            'http://localhost:8000/api/auth/signup/',
            json={
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'company_name': 'Test Company',
            }
        )
        self.assertEqual(signup_response.status_code, 201)
        user_data = signup_response.json()

        # 2. Login (Identity Service)
        login_response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json={
                'email': 'test@example.com',
                'password': 'testpass123',
            }
        )
        self.assertEqual(login_response.status_code, 200)
        tokens = login_response.json()
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}

        # 3. Create client (Project Service)
        client_response = requests.post(
            'http://localhost:8000/api/clients/',
            json={
                'name': 'Test Client',
                'email': 'client@example.com',
                'status': 'prospect',
            },
            headers=headers
        )
        self.assertEqual(client_response.status_code, 201)
        client_id = client_response.json()['id']

        # 4. Create project (Project Service)
        project_response = requests.post(
            'http://localhost:8000/api/projects/',
            json={
                'name': 'Test Project',
                'client_id': client_id,
                'status': 'planning',
            },
            headers=headers
        )
        self.assertEqual(project_response.status_code, 201)
        project_id = project_response.json()['id']

        # 5. Create invoice (Accounting Service)
        invoice_response = requests.post(
            'http://localhost:8000/api/invoices/',
            json={
                'client_id': client_id,
                'project_id': project_id,
                'amount': '1000.00',
                'currency': 'USD',
                'status': 'draft',
            },
            headers=headers
        )
        self.assertEqual(invoice_response.status_code, 201)

        # 6. Verify audit log created (Audit Service)
        time.sleep(2)  # Wait for event processing
        audit_response = requests.get(
            'http://localhost:8000/api/audit/logs/',
            headers=headers
        )
        self.assertTrue(
            any(log['action'] == 'invoice.created' for log in audit_response.json())
        )

        # 7. Verify email sent (check RabbitMQ)
        # ... verify email event was published
```

### Performance Testing

**Load Test with Locust:**
```python
# tests/performance/load_test.py
from locust import HttpUser, task, between

class CRMUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login on start"""
        response = self.client.post("/api/auth/login/", json={
            "email": "test@example.com",
            "password": "testpass123",
        })
        if response.status_code == 200:
            self.token = response.json()['access_token']

    @task(3)
    def list_clients(self):
        """List clients (frequent operation)"""
        self.client.get("/api/clients/", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(2)
    def list_projects(self):
        """List projects (medium frequency)"""
        self.client.get("/api/projects/", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(1)
    def create_invoice(self):
        """Create invoice (less frequent)"""
        self.client.post("/api/invoices/", json={
            "client_id": "some-uuid",
            "amount": "1000.00",
            "currency": "USD",
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })
```

---

## Deployment Strategy

### Local Development

```bash
# Option 1: All services in Docker (easiest)
make docker-up-microservices

# Option 2: Hybrid (services local, infra in Docker)
docker-compose up -d postgres-* rabbitmq redis

# Then run services locally
cd services/identity-service && python manage.py runserver 8001
cd services/audit-service && python manage.py runserver 8002
# etc.

# Option 3: All services local (for development)
# Run services with local processes
# Terminal 1
cd services/identity-service && python manage.py runserver 8001

# Terminal 2
cd services/audit-service && python manage.py runserver 8002

# etc.
```

### Production Deployment (Docker Swarm)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Infrastructure (external services)
  postgres-identity:
    image: postgres:15
    deploy:
      replicas: 1
    environment:
      POSTGRES_DB: identity_db
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - identity_data:/var/lib/postgresql/data
    networks:
      - backend

  # Services with scaling
  identity-service:
    image: crm-identity-service:latest
    deploy:
      replicas: 3  # Scale based on load
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres-identity:5432/identity_db
      RABBITMQ_URL: amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@rabbitmq:5672/
    networks:
      - backend
    depends_on:
      - postgres-identity

  audit-service:
    image: crm-audit-service:latest
    deploy:
      replicas: 5  # High write volume, need more replicas
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
    # ... similar config

networks:
  backend:
    driver: overlay

volumes:
  identity_data:
  audit_data:
  # etc.
```

### CI/CD Pipeline

```yaml
# .github/workflows/microservices.yml
name: Microservices CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [identity, audit, project, accounting, hr, sales]

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Run tests for ${{ matrix.service }}
        run: |
          cd backend/services/${{ matrix.service }}-service
          pip install -r requirements.txt
          python manage.py test

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [identity, audit, project, accounting, hr, sales]

    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: |
          docker build -t crm-${{ matrix.service }}-service:${{ github.sha }} \
            -f backend/services/${{ matrix.service }}-service/Dockerfile \
            backend/services/${{ matrix.service }}-service

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push crm-${{ matrix.service }}-service:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        run: |
          # SSH into server
          ssh user@server.com

          # Pull new images
          docker-compose -f docker-compose.prod.yml pull

          # Restart services
          docker-compose -f docker-compose.prod.yml up -d

          # Verify health
          curl -f http://crm.example.com/api/health/
```

---

## Rollback Plan

### Option A: Parallel Running (Recommended)

**During Migration:**
- Keep monolith running alongside microservices
- Use feature flags to route traffic gradually
- API Gateway can route some requests to monolith, others to microservices

**Rollback:**
- Switch feature flags back to monolith
- All traffic goes back to monolith immediately
- No data loss (fresh databases)

### Option B: Big Bang Cutover

**During Migration:**
- Develop microservices in parallel
- Test thoroughly before cutover

**Rollback:**
- Restore database backup
- Redeploy monolith
- Data loss possible if not careful

---

## Risk Assessment & Mitigation

### Risk 1: Data Consistency Across Services
**Impact:** High
**Mitigation:**
- Eventual consistency model
- Saga pattern for multi-step transactions
- Regular data reconciliation jobs
- Monitoring for data drift

### Risk 2: Network Latency
**Impact:** Medium
**Mitigation:**
- Cache frequently accessed data (users, tenants)
- Use synchronous calls only when necessary
- Deploy services in same region/VPC
- Optimize service-to-service calls

### Risk 3: Single Developer Overhead
**Impact:** High
**Mitigation:**
- Comprehensive documentation
- Shared libraries for common patterns
- Automated testing and deployment
- Realistic timeline with buffer
- Focus on high-value services first

### Risk 4: Service Discovery & Communication
**Impact:** Medium
**Mitigation:**
- API Gateway handles routing
- Service registry (Consul/Etcd)
- Circuit breakers for resilience
- Health checks and monitoring

### Risk 5: Testing Complexity
**Impact:** Medium
**Mitigation:**
- Integration test suite
- Contract testing between services
- End-to-end testing framework
- Performance testing baseline

### Risk 6: Operational Complexity
**Impact:** High
**Mitigation:**
- Docker Compose for local development
- Infrastructure as code
- Monitoring and alerting
- Runbooks and troubleshooting guides

---

## Success Criteria

**Week 12 Completion Requirements:**

1. ✅ **All 7 services are running** with separate databases
2. ✅ **API Gateway routes traffic** correctly with middleware (JWT auth, rate limiting, CORS)
3. ✅ **JWT authentication works** across all services with service-to-service auth
4. ✅ **Event-driven communication** via RabbitMQ (all exchanges active with DLQ)
5. ✅ **Audit logs captured** from all services with correlation IDs
6. ✅ **Email notifications work** via event-driven architecture
7. ✅ **Data migration completed** without loss (fresh DBs)
8. ✅ **Distributed tracing** working across service calls (Jaeger)
9. ✅ **Monitoring stack** collecting metrics from all services (Prometheus + Grafana)
10. ✅ **Centralized logging** with ELK stack operational
11. ✅ **Circuit breakers** protecting all service-to-service calls
12. ✅ **Contract tests** passing between all service pairs
13. ✅ **Chaos engineering** tests completed without critical failures
14. ✅ **Data consistency** validated across all services
15. ✅ **Performance benchmarks** meeting requirements (1000+ events/sec)
16. ✅ **Frontend unchanged** - all APIs accessible without changes
17. ✅ **Services scale independently** with load balancing
18. ✅ **Documentation complete** with runbooks and troubleshooting
19. ✅ **CI/CD pipeline** deploying all services automatically
20. ✅ **Backup/restore** procedures tested and documented
21. ✅ **RTO/RPO** requirements met for each service

**Week 1 Completion Requirements (Event Bus):**
1. ✅ **Event Bus fully implemented** with all critical fixes
2. ✅ **Event publishing/consuming tested** across services
3. ✅ **Thread safety validated** under concurrent load
4. ✅ **Dead letter queue configured** and monitored
5. ✅ **Async publishing working** without blocking requests
6. ✅ **Retry logic tested** with simulated failures
7. ✅ **Circuit breaker integrated** with event publishing
8. ✅ **Correlation ID tracking** working across events
9. ✅ **Event validation** with Pydantic schemas
10. ✅ **Metrics/monitoring** integrated with event bus

---

## Documentation Structure

New documentation to create:

```
docs/microservices/
├── MICROSERVICES_MIGRATION_PLAN.md (this file)
├── architecture.md              # Overall architecture diagram
├── service-boundaries.md        # Which service owns which data
├── communication.md             # Sync vs async communication
├── event-schemas.md            # All event types and schemas
├── database-schema.md          # ER diagrams for each DB
├── authentication.md           # JWT and service auth
├── deployment.md              # Deployment strategies
├── local-development.md        # How to run locally
├── testing.md                # Testing strategies
├── monitoring.md              # Metrics and alerts
├── troubleshooting.md         # Common issues and solutions
└── migration/                # Migration-specific docs
    ├── data-migration.md
    ├── validation.md
    ├── rollback.md
    └── cutover.md
```

---

## Code Structure to Create

```
backend/
├── services/
│   ├── identity-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── manage.py
│   │   └── identity_service/
│   │       ├── models/
│   │       ├── serializers/
│   │       ├── views/
│   │       ├── services/
│   │       └── consumers/
│   ├── audit-service/
│   ├── notification-service/
│   ├── project-service/
│   ├── accounting-service/
│   ├── hr-service/
│   └── sales-service/
├── shared/
│   ├── event_bus.py          # Event publishing/consuming
│   ├── jwt_utils.py         # JWT token validation
│   ├── service_client.py    # HTTP client for inter-service calls
│   ├── models.py            # Shared data models (DTOs)
│   ├── exceptions.py        # Custom exceptions
│   └── circuit_breaker.py   # Circuit breaker pattern
└── scripts/
    ├── export_monolith_data.sh
    ├── transform_data_for_microservices.py
    ├── import_to_services.sh
    └── validate_data_migration.py
```

---

## Next Steps

1. **Review and Approve Plan** - Confirm timeline, scope, and approach
2. **Create Feature Branch** - `git checkout -b feature/microservices-migration`
3. **Start Phase 1** - Infrastructure setup and Event Bus hardening (Weeks 1-2)
4. **Weekly Checkpoints** - Review progress and adjust as needed
5. **Final Cutover** - Week 12, full microservices deployment

---

**Questions for Final Approval**

1. **Timeline**: 12 weeks acceptable, or prefer 10 weeks (higher risk) or 14 weeks (more buffer)?
2. **Event Bus Priority**: Week 1 focus on Event Bus fixes - acceptable?
3. **Communication Strategy**: Cached metadata pattern preferred, or want to explore API composition more?
4. **Transaction Management**: Saga patterns for accounting, or prefer simpler eventual consistency?
5. **Monitoring**: Full ELK + Jaeger + Prometheus stack, or prefer simpler setup?
6. **Migration Order**: Identity+Audit together, then Notification POC - does this make sense?
7. **Testing**: Contract testing + chaos engineering - appropriate level for your team?

**The plan now addresses all critical Event Bus issues and provides a robust, production-ready migration strategy. Ready to proceed with implementation?**

**Timeline starts with Event Bus hardening on Day 3-4, ensuring we have reliable inter-service communication from the beginning.** 🚀