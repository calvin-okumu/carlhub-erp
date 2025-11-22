# Leave Management



DjangoCRM provides comprehensive leave management functionality for tracking employee time off, managing leave balances, and enforcing company leave policies. The system supports various leave types, configurable approval workflows with up to 5 levels, automatic HR fallback approval, and full integration with payroll and HR systems.



## Overview



### Key Features



- **Multiple Leave Types**: Annual leave, sick leave, maternity/paternity leave, emergency leave, and unpaid leave

- **Configurable Approval Workflows**: HR-configurable multi-level approval processes (up to 5 levels) with role-based, user-specific, and group-based approvals

- **Default HR Approval**: Automatic fallback to HR approval when no workflow is configured

- **Leave Balance Tracking**: Real-time balance monitoring with carry-over rules

- **Policy Management**: Company-wide leave policies with flexible rules

- **Calendar Integration**: Leave calendar views and conflict detection

- **Reporting**: Comprehensive leave usage reports and analytics



### Business Benefits



- **Compliance**: Ensure adherence to labor laws and company policies

- **Planning**: Better workforce planning with visibility into team availability

- **Cost Control**: Track leave costs and manage budgets effectively

- **Employee Satisfaction**: Fair and transparent leave management processes

- **Flexible Approvals**: Configurable workflows adapt to different leave types and organizational structures

- **Automated Routing**: Reduce manual coordination with intelligent approval routing



## Leave Types



### Supported Leave Categories



- **Annual Leave**: Standard vacation time accrued annually

- **Sick Leave**: Medical absence with or without pay

- **Personal Leave**: Personal time off for various reasons

- **Maternity/Paternity Leave**: Parental leave for new parents

- **Emergency Leave**: Unplanned absences due to emergencies

- **Unpaid Leave**: Leave without pay for extended absences



### Leave Policies



Each tenant can configure leave policies including:



- **Entitlement**: Annual leave allocation (days per year)

- **Carry-over Rules**: How unused leave transfers to the next year

- **Notice Periods**: Minimum advance notice required

- **Maximum Consecutive Days**: Limits on continuous leave periods

- **Auto-approval Thresholds**: Automatic approval for short absences



## Leave Request Workflow



### Request Submission



Employees submit leave requests specifying:



- Leave type and dates

- Reason for absence

- Expected contact information (if needed)



### Approval Process



1. **Submission**: Employee creates leave request

2. **Workflow Determination**:
   - Check for leave-type specific workflow
   - Fall back to tenant default workflow
   - Default to HR approval if no workflow configured

3. **Multi-Level Approval**: Request progresses through configured approval levels

4. **Manager Review**: Designated approvers review at each level

5. **Approval/Rejection**: Manager approves or rejects with notes (approver automatically recorded)

6. **Balance Update**: Approved leave deducts from employee balance

7. **Notification**: All parties receive email notifications



### Automated Rules



- **Business Day Calculation**: Leave days exclude weekends

- **Overlap Detection**: Prevents conflicting leave requests

- **Balance Validation**: Ensures sufficient leave balance

- **Policy Enforcement**: Applies company leave policies automatically

- **Workflow Routing**: Automatic determination of approval workflow based on leave type and tenant defaults



## Leave Balances



### Balance Tracking



- **Annual Entitlement**: Base leave allocation per year

- **Used Days**: Leave days already taken

- **Remaining Days**: Available leave balance

- **Carry-over**: Unused leave from previous years

- **Utilization Rate**: Percentage of leave used vs. allocated



### Balance Management



- **Automatic Updates**: Balances update when leave is approved

- **Year-end Processing**: Carry-over calculations and resets

- **Manual Adjustments**: HR can adjust balances for special cases

- **Reporting**: Balance reports for employees and management


## Approval Workflows


### Overview

DjangoCRM supports configurable approval workflows that allow HR to define multi-level approval processes for leave requests. Workflows can be configured per leave type or set as tenant defaults.

### Key Features

- **Multi-Level Approvals**: Up to 5 approval levels per workflow (configurable limit)
- **Flexible Approvers**: Support for role-based, user-specific, and group-based approvals
- **Tenant-Scoped**: Workflows are configured per tenant
- **Default Fallback**: Automatic HR approval when no workflow is configured
- **Workflow Inheritance**: Leave-type specific workflows override tenant defaults

### Approval Types

#### Role-Based Approval
Approves based on user roles (Department Manager, HR Manager, General Manager, etc.)

#### User-Specific Approval
Assigns specific users as approvers

#### Permission Group Approval
Approves based on membership in permission groups

#### Dynamic Approvals
- **Department Manager**: Employee's department manager
- **Dynamic HR**: Automatic HR selection
- **Dynamic GM**: Automatic General Manager selection

### Default Behavior

When no workflow is configured, the system defaults to HR approval:

1. **Primary**: HR Manager role
2. **Fallback**: General Manager or Tenant Owner roles
3. **Emergency**: Any approved user with elevated permissions

### Workflow Configuration

HR can configure workflows through the admin interface or API:

1. **Create Workflow**: Define workflow name and description
2. **Add Levels**: Configure up to 5 approval levels
3. **Assign Approvers**: Select approval type and specific approvers for each level
4. **Set Default**: Mark workflow as tenant default
5. **Associate with Leave Types**: Link workflows to specific leave types via policies

### Workflow Priority and Inheritance

The system follows a priority hierarchy when determining which workflow to use:

1. **Leave-Type Specific**: Workflow linked to the specific leave type (highest priority)
2. **Tenant Default**: Default workflow for the tenant
3. **HR Fallback**: Automatic HR approval when no workflow is configured (lowest priority)

**Example:**
- Annual leave → Uses annual leave workflow (if configured) → Falls back to tenant default → Falls back to HR approval
- Maternity leave → Uses maternity workflow → Falls back to tenant default → Falls back to HR approval

This ensures all leave requests have a defined approval path while allowing flexibility for different leave types.



## Integration Points



### HR Systems



- **Employee Data**: Sync with HR systems for employee information

- **Payroll Integration**: Leave data feeds into payroll calculations

- **Compliance Reporting**: Generate reports for regulatory compliance



### Calendar Systems



- **Outlook/Google Calendar**: Sync leave events to employee calendars

- **Team Calendars**: Shared calendars showing team availability

- **Conflict Prevention**: Detect scheduling conflicts



### Notification Systems



- **Email Notifications**: Automated emails for request status changes

- **Slack/Teams Integration**: Real-time notifications in chat systems

- **Mobile Alerts**: Push notifications for urgent approvals



## Reporting and Analytics



### Management Reports



- **Leave Usage Summary**: Overall leave patterns and trends

- **Department Reports**: Leave usage by department

- **Compliance Reports**: Policy adherence and exceptions

- **Cost Analysis**: Leave costs and budget impact



### Employee Self-Service



- **Balance Dashboard**: Current leave balances and usage

- **Request History**: Past leave requests and status

- **Calendar View**: Visual leave calendar

- **Policy Information**: Access to leave policies and rules



## Best Practices



### Policy Design



1. **Clear Guidelines**: Well-documented leave policies

2. **Fair Allocation**: Equitable leave entitlements

3. **Flexibility**: Accommodate different employee needs

4. **Compliance**: Adhere to local labor laws



### Process Management



1. **Timely Approvals**: Quick response to leave requests

2. **Communication**: Clear communication throughout the process

3. **Documentation**: Maintain records of all leave transactions

4. **Training**: Educate employees and managers on processes

### Workflow Configuration Best Practices



1. **Keep It Simple**: Use 1-3 approval levels for most leave types

2. **Role-Based Approvals**: Prefer role-based approvals over specific users for scalability

3. **Escalation Path**: Ensure clear escalation from department → HR → executive levels

4. **Default Workflows**: Configure tenant-wide defaults for common leave types

5. **Leave-Type Specific**: Use specialized workflows for unique leave types (maternity, sabbatical)

6. **Regular Review**: Periodically review and update workflows as organization changes

7. **Testing**: Test workflows with sample requests before going live



### System Administration



1. **Regular Audits**: Review leave data for accuracy

2. **Policy Updates**: Keep policies current with regulations

3. **Data Backup**: Regular backups of leave data

4. **Access Control**: Secure access to sensitive leave information

5. **Workflow Maintenance**: Regularly review and update approval workflows

6. **User Role Management**: Ensure user roles are correctly assigned for workflow approvals

7. **Performance Monitoring**: Monitor approval response times and workflow bottlenecks



---




## 🗓️ Leave Management

### Leave Requests

#### List Leave Requests
**GET** `/api/leave/requests/`

List leave requests with filtering and search.

**Query Parameters:**
- `status` - Filter by status (pending_department_manager, pending_hr_manager, pending_general_manager, approved, rejected, cancelled, taken)
- `status__in` - Filter by multiple statuses (e.g., pending_department_manager,pending_hr_manager)
- `leave_type` - Filter by leave type (annual_leave, sick_leave, etc.)
- `employee` - Filter by employee UUID
- `approved_by` - Filter by approver UUID
- `start_date` - Filter by start date range
- `end_date` - Filter by end date range

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/leave/requests/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "leave-uuid-2024-01-15",
      "employee": {
        "id": "uuid",
        "email": "employee@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "start_date": "2024-01-15",
      "end_date": "2024-01-19",
      "days_requested": "5.0",
      "reason": "Vacation time",
      "status": "pending",
      "applied_date": "2024-01-10T09:00:00Z",
      "approved_by": null,
      "approved_date": null,
      "approval_notes": "",
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-10T09:00:00Z"
    }
  ]

}
```

#### Get Pending Approvals for Managers
**GET** `/api/leave/requests/?status__in=pending_department_manager,pending_hr_manager,pending_general_manager`

Managers can retrieve leave requests pending their approval using status filters. The response includes a `can_approve` field indicating which requests the current user has authority to approve.

**Query Parameters for Pending Approvals:**
- `status=pending_department_manager` - Requests pending department manager approval
- `status=pending_hr_manager` - Requests pending HR manager approval
- `status=pending_general_manager` - Requests pending general manager approval
- `status__in=pending_department_manager,pending_hr_manager,pending_general_manager` - All pending requests

**Role-Based Access:**
- **Department Managers**: Can approve requests from employees in their department
- **HR Managers**: Can approve department-level and HR-level requests
- **General Managers/Tenant Owners**: Can approve requests at all levels

**Response includes:**
- `can_approve`: Boolean indicating if current user can approve this request
- `current_approver`: Name of the designated approver
- `workflow_status`: Detailed approval workflow information

**Example - Get all pending approvals:**
```
GET /api/leave/requests/?status__in=pending_department_manager,pending_hr_manager,pending_general_manager
```

#### Create Leave Request
**POST** `/api/leave/requests/`

Create a new leave request.

**Request:**
```json
{
  "leave_type": "annual_leave",
  "start_date": "2024-01-15",
  "end_date": "2024-01-19",
  "reason": "Vacation time"
}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "leave-uuid-2024-01-15",
  "employee": "uuid",
  "tenant": "uuid",
  "leave_type": "annual_leave",
  "start_date": "2024-01-15",
  "end_date": "2024-01-19",
  "days_requested": "5.0",
  "reason": "Vacation time",
  "status": "pending",
  "applied_date": "2024-01-10T09:00:00Z",
  "approved_by": null,
  "approved_date": null,
  "approval_notes": "",
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-10T09:00:00Z"
}
```

#### Get Leave Request
**GET** `/api/leave/requests/{slug}/`

Get detailed leave request information.

**Error Responses:**
- `404 Not Found`: `{"detail": "Leave request not found."}` (if slug doesn't exist)

#### Update Leave Request
**PUT/PATCH** `/api/leave/requests/{slug}/`

Update leave request (only by employee, only if pending).

#### Delete Leave Request
**DELETE** `/api/leave/requests/{slug}/`

Delete leave request (only by employee, only if pending).

#### Approve Leave Request (Legacy)
**POST** `/api/leave/requests/{slug}/approve/`

**⚠️ Deprecated**: Use `approve_level/` endpoint instead for proper workflow support.

Approve a leave request (managers only).

**Request:**
```json
{
  "notes": "Approved for vacation"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "approved",
  "approved_by": "uuid",
  "approved_date": "2024-01-11T10:00:00Z",
  "approval_notes": "Approved for vacation"
}
```

#### Reject Leave Request (Legacy)
**POST** `/api/leave/requests/{slug}/reject/`

**⚠️ Deprecated**: Use `reject_level/` endpoint instead for proper workflow support.

Reject a leave request (managers only).

**Request:**
```json
{
  "notes": "Insufficient notice period"
}
```

#### Cancel Leave Request
**POST** `/api/leave/requests/{slug}/cancel/`

Cancel a leave request (only by the employee who created it).

#### Approve at Current Level
**POST** `/api/leave/requests/{slug}/approve_level/`

Approve a leave request at the current workflow level (managers only). The logged-in user is automatically recorded as the approver.

**Request:**
```json
{
  "notes": "Approved for vacation"
}
```

**Response:**
```json
{
  "message": "Approved at department_manager level. Now pending hr_manager approval.",
  "data": {...},
  "next_level": "hr_manager"
}
```

#### Reject at Current Level
**POST** `/api/leave/requests/{slug}/reject_level/`

Reject a leave request at the current workflow level (managers only). The logged-in user is automatically recorded as the approver.

**Request:**
```json
{
  "notes": "Insufficient notice period"
}
```

#### Get Workflow Status
**GET** `/api/leave/requests/{slug}/workflow_status/`

Get detailed workflow status and approval history for a leave request.

**Response:**
```json
{
  "workflow_status": {
    "current_status": "Pending Department Manager Approval",
    "current_level": "department_manager",
    "is_pending": true,
    "is_approved": false,
    "is_rejected": false,
    "steps": [
      {
        "level": "department_manager",
        "level_display": "Department Manager",
        "approver": "John Manager",  // Shows the actual user who approved (when completed)
        "status": "pending",
        "approved_date": null,
        "notes": "",
        "order": 1
      }
    ],
    "next_approver": "John Manager"
  },
  "approval_history": [...]
}
```

### Leave Balances

#### List Leave Balances
**GET** `/api/leave/balances/`

List leave balances for employees.

**Query Parameters:**
- `employee` - Filter by employee UUID
- `leave_type` - Filter by leave type
- `year` - Filter by year

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "employee": {
        "id": "uuid",
        "email": "employee@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "year": 2024,
      "total_days": "25.0",
      "used_days": "5.0",
      "remaining_days": "20.0",
      "utilization_percentage": 20.0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T00:00:00Z"
    }
  ]
}
```

#### Get Leave Balance
**GET** `/api/leave/balances/{slug}/`

Get specific leave balance details.

#### Update Leave Balance
**PUT/PATCH** `/api/leave/balances/{slug}/`

Update leave balance (HR/admin only).

#### Create Leave Balance
**POST** `/api/leave/balances/`

Create new leave balance entry (HR/admin only).

### Leave Policies

#### List Leave Policies
**GET** `/api/leave/policies/`

List leave policies for the tenant.

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "annual_entitlement": "25.0",
      "max_consecutive_days": 30,
      "notice_period_days": 7,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Leave Policy
**GET** `/api/leave/policies/{slug}/`

Get specific leave policy details.

#### Create Leave Policy
**POST** `/api/leave/policies/`

Create new leave policy (admin only).

**Request:**
```json
{
  "leave_type": "annual_leave",
  "annual_entitlement": "25.0",
  "max_consecutive_days": 30,
  "notice_period_days": 7
}
```

#### Update Leave Policy
**PUT/PATCH** `/api/leave/policies/{slug}/`

Update leave policy (admin only).

#### Delete Leave Policy
**DELETE** `/api/leave/policies/{slug}/`

Delete leave policy (admin only).

### Approval Workflows

#### List Workflows
**GET** `/api/leave/workflows/`

List approval workflows for the tenant.

**Query Parameters:**
- `is_active` - Filter by active status (true/false)
- `is_default` - Filter by default status (true/false)

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Standard Approval Workflow",
      "description": "Two-level approval process",
      "is_default": true,
      "is_active": true,
      "number_of_levels": 2,
      "level_configs": [
        {
          "id": "uuid",
          "level": 1,
          "approval_type": "role",
          "approval_type_display": "By Role",
          "required_role": "Department Manager",
          "required_role_display": "Department Manager"
        },
        {
          "id": "uuid",
          "level": 2,
          "approval_type": "role",
          "approval_type_display": "By Role",
          "required_role": "HR Manager",
          "required_role_display": "HR Manager"
        }
      ],
      "created_by": "uuid",
      "created_by_name": "John Doe",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Create Workflow
**POST** `/api/leave/workflows/`

Create a new approval workflow (maximum 5 approval levels).

**Request:**
```json
{
  "name": "Executive Leave Workflow",
  "description": "Special approval for executive leave",
  "is_default": false,
  "is_active": true,
  "level_configs": [
    {
      "level": 1,
      "approval_type": "role",
      "required_role": "Department Manager"
    },
    {
      "level": 2,
      "approval_type": "role",
      "required_role": "HR Manager"
    },
    {
      "level": 3,
      "approval_type": "role",
      "required_role": "General Manager"
    }
  ]
}
```

**Validation:**
- Maximum 5 levels per workflow
- Valid approval types: `user`, `permission_group`, `role`, `department_manager`, `dynamic_hr`, `dynamic_gm`
- Required fields based on approval type

**Response:** Same as list response format.

#### Get Workflow
**GET** `/api/leave/workflows/{id}/`

Get detailed workflow information.

#### Update Workflow
**PUT/PATCH** `/api/leave/workflows/{id}/`

Update workflow configuration.

#### Delete Workflow
**DELETE** `/api/leave/workflows/{id}/`

Delete workflow (admin only).

#### Set Default Workflow
**POST** `/api/leave/workflows/{id}/set_default/`

Set this workflow as the tenant default.

**Response:**
```json
{
  "message": "Workflow set as default",
  "workflow": {...}
}
```

#### Get Level Configurations
**GET** `/api/leave/workflows/{id}/level_configs/`

Get level configurations for a workflow.

#### Update Level Configurations
**PUT** `/api/leave/workflows/{id}/update_configs/`

Update level configurations for a workflow.

**Request:**
```json
{
  "level_configs": [
    {
      "level": 1,
      "approval_type": "user",
      "specific_user": "uuid"
    },
    {
      "level": 2,
      "approval_type": "permission_group",
      "permission_group": "uuid"
    }
  ]
}
```

#### Get Approval Analytics
**GET** `/api/leave/workflows/analytics/`

Get approval workflow analytics for the tenant.

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

#### Get Notifications Summary
**GET** `/api/leave/workflows/notifications_summary/`

Get summary of pending approvals for the current user.

#### Send Approval Reminders
**POST** `/api/leave/workflows/send_reminders/`

Send reminder notifications for pending approvals (HR/Admin only).

#### Send Escalation Notifications
**POST** `/api/leave/workflows/send_escalations/`

Send escalation notifications for critically overdue requests (Admin only).

#### Quick Approve Request
**POST** `/api/leave/workflows/{id}/quick_approve/`

Quick approve a leave request with minimal data (mobile-friendly).

#### Quick Reject Request
**POST** `/api/leave/workflows/{id}/quick_reject/`

Quick reject a leave request (mobile-friendly).

**Request:**
```json
{
  "reason": "Insufficient leave balance"
}
```

### Management Commands

#### Initialize Leave Balances
**Management Command:** `python manage.py initialize_leave_balances`

Initialize annual leave balances for all employees across tenants.

**Options:**
- `--tenant` - Specific tenant slug
- `--dry-run` - Preview changes without applying

#### Carry Over Leave Balances
**Management Command:** `python manage.py carry_over_leave_balances`

Perform year-end carry-over of unused leave days.

**Options:**
- `--tenant` - Specific tenant slug
- `--dry-run` - Preview changes without applying

#### Leave Reporting
**Management Command:** `python manage.py leave_reporting`

Generate HR reports on leave usage and compliance.

**Options:**
- `--tenant` - Specific tenant slug
- `--output` - Output file path
- `--summary` - Summary report only
