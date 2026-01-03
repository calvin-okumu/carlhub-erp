# CRM Core

The foundation application of DjangoCRM providing essential customer relationship management, user management, and system administration capabilities.

## User Journey & Operational Flow

### 1. Account Creation & Onboarding

#### New User Registration
```
User visits website → Signs up with email → Receives verification → Sets up profile
```
- **Email Verification**: Required for account activation
- **Profile Setup**: Name, company details, role selection
- **Password Security**: Strong password requirements enforced

#### Organization Setup
```
User creates tenant (organization) → Defines company details → Invites team members
```
- **Tenant Creation**: Company name, domain, industry, size
- **Team Invitations**: Email-based invites with role assignment
- **Permission System**: Granular access control (Owner, Manager, Employee, etc.)

### 2. Authentication & Access

#### Login Process
```
User enters credentials → JWT token generated → Tenant context established → Dashboard access
```
- **Multi-tenant Isolation**: Each user sees only their organization's data
- **Role-based Access**: Permissions filter available features
- **Session Management**: Secure token-based authentication

### 3. Main Dashboard & Navigation

#### Post-Login Experience
```
Dashboard loads → Shows key metrics → Navigation to modules → Quick actions available
```
- **Analytics Overview**: Pipeline value, active projects, team performance
- **Quick Stats**: Revenue, project completion, leave balances
- **Module Access**: Projects, Sales, Leave Management, Financials

### 4. Core Operational Workflows

#### 🏗️ Project Management Flow
```
Client Onboarding → Project Creation → Milestone Planning → Task Assignment → Progress Tracking → Invoice Generation
```

1. **Client Management**
   - Add new clients with contact details
   - Track client history and projects
   - Manage contracts and agreements

2. **Project Lifecycle**
   - Create project with scope and budget
   - Define milestones and deliverables
   - Assign team members and deadlines
   - Track progress with time logging

3. **Financial Integration**
   - Generate invoices automatically
   - Track payments and outstanding amounts
   - Financial reporting and analytics

#### 💼 Sales Management Flow
```
Lead Generation → Customer Qualification → Opportunity Creation → Pipeline Management → Deal Closure → Post-sale Support
```

1. **Lead Management**
   - Import or manually add prospects
   - Score leads based on criteria
   - Track lead sources and campaigns

2. **Sales Pipeline**
   - Convert leads to opportunities
   - Advance through sales stages
   - Track probability and expected close dates
   - Log all customer interactions

3. **Team Collaboration**
   - Assign opportunities to sales reps
   - Share customer insights
   - Coordinate follow-ups and demos

#### 📅 Leave Management Flow
```
Leave Request → Manager Approval → HR Review → Calendar Update → Payroll Integration
```

1. **Leave Planning**
   - View leave balances and policies
   - Submit leave requests with dates
   - Attach supporting documentation

2. **Approval Workflow**
   - Manager review and approval
   - HR oversight for policy compliance
   - Automated notifications

3. **Calendar Integration**
   - Team calendar updates
   - Absence tracking
   - Coverage planning

### 5. Daily User Operations

#### Morning Routine
```
Login → Check dashboard metrics → Review assigned tasks → Check notifications → Plan day's work
```

#### Task Execution
```
Open assigned projects/tasks → Update progress → Log time spent → Communicate with team → Complete deliverables
```

#### Communication & Collaboration
```
Team chat/messaging → File sharing → Progress updates → Client communications → Meeting scheduling
```

### 6. Administrative Operations

#### System Management
```
User management → Permission assignment → System configuration → Data backups → Compliance monitoring
```

#### Reporting & Analytics
```
Generate reports → Export data → Performance analysis → Trend identification → Strategic planning
```

### 7. Integration Points

#### External Systems
```
Email integration → Calendar sync → Document storage → Payment gateways → Third-party APIs
```

#### Mobile Access
```
Responsive web interface → Mobile-optimized views → Offline capabilities → Push notifications
```

### 8. Support & Help

#### Self-Service
```
In-app help → Documentation → Video tutorials → FAQ section → Community forums
```

#### Customer Support
```
Help desk tickets → Live chat → Phone support → Training sessions → Feature requests
```

### Key User Personas & Their Flows

#### 👨‍💼 Sales Representative
```
Login → Check pipeline → Update opportunities → Log activities → Schedule follow-ups → Close deals
```

#### 👩‍💼 Project Manager
```
Login → Review project status → Assign tasks → Track milestones → Manage resources → Client updates
```

#### 🏢 HR Manager
```
Login → Review leave requests → Approve/reject requests → Manage policies → Generate reports → Team planning
```

#### 💼 Company Owner/CEO
```
Login → View executive dashboard → Review KPIs → Strategic planning → Team performance → Financial overview
```

### Getting Started Checklist

#### For New Organizations
1. ✅ Create tenant account
2. ✅ Set up company profile
3. ✅ Invite team members
4. ✅ Configure permissions
5. ✅ Import existing data
6. ✅ Set up integrations
7. ✅ Train team members
8. ✅ Go live!

#### For Individual Users
1. ✅ Receive invitation email
2. ✅ Set up profile and password
3. ✅ Complete onboarding tutorial
4. ✅ Explore assigned modules
5. ✅ Start using core features
6. ✅ Connect with team members

## Core Features

### User Management
- Multi-tenant user registration and authentication
- Role-based access control (Owner, Manager, Employee, Client)
- User profile management with extended information
- Employee document storage and management

### Client Management
- Client relationship database
- Contact information and company details
- Client status tracking (Active, Inactive, Prospect)
- Client history and interaction logging

### System Administration
- Tenant management and configuration
- System-wide settings and preferences
- User permission and role assignment
- Audit logging and compliance tracking

## Architecture

### Data Models
- **CustomUser**: Extended Django user with soft delete
- **Tenant**: Multi-tenant organization container
- **UserTenant**: User-tenant membership relationships
- **Client**: Customer/organization records
- **UserProfile**: Extended user information
- **EmployeeDocument**: Document storage for employees

### Key Components
- **Authentication System**: JWT-based API authentication
- **Permission Framework**: Custom permission groups and assignments
- **Audit System**: Comprehensive logging of all user actions
- **Email Service**: Professional email templates and delivery

## API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/signup/` - User registration
- `GET /api/auth-methods/` - Available auth methods

### User Management
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile

### Client Management
- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client
- `PUT /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client

### Invitations
- `POST /api/invite-member/` - Invite new member
- `POST /api/resend-invitation/` - Resend invitation
- `POST /api/confirm-invitation/` - Confirm email
- `GET /api/invitations/` - List invitations

## Security Features

### Data Isolation
- Complete tenant data separation
- Row-level security on all queries
- Permission-based access control

### Audit Trail
- All user actions logged
- IP address tracking
- Timestamp recording
- Compliance reporting

### Authentication
- Secure password hashing
- JWT token management
- Session timeout handling
- Failed login monitoring

## Integration Points

### Project Tracker
- User data synchronization
- Client data sharing
- Permission inheritance

### Financial Suite
- User access to financial data
- Client billing information
- Invoice permissions

### Admin Panel
- User management interface
- System configuration
- Audit log access
