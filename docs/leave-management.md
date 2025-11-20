# Leave Management



DjangoCRM provides comprehensive leave management functionality for tracking employee time off, managing leave balances, and enforcing company leave policies. The system supports various leave types, automated approval workflows, and integration with payroll and HR systems.



## Overview



### Key Features



- **Multiple Leave Types**: Annual leave, sick leave, maternity/paternity leave, emergency leave, and unpaid leave

- **Automated Approval Workflows**: Configurable multi-level approval processes with automatic approver tracking

- **Leave Balance Tracking**: Real-time balance monitoring with carry-over rules

- **Policy Management**: Company-wide leave policies with flexible rules

- **Calendar Integration**: Leave calendar views and conflict detection

- **Reporting**: Comprehensive leave usage reports and analytics



### Business Benefits



- **Compliance**: Ensure adherence to labor laws and company policies

- **Planning**: Better workforce planning with visibility into team availability

- **Cost Control**: Track leave costs and manage budgets effectively

- **Employee Satisfaction**: Fair and transparent leave management processes



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

2. **Manager Review**: Designated approvers review the request

3. **Approval/Rejection**: Manager approves or rejects with notes (approver automatically recorded as the logged-in user)

4. **Balance Update**: Approved leave deducts from employee balance

5. **Notification**: All parties receive email notifications



### Automated Rules



- **Business Day Calculation**: Leave days exclude weekends

- **Overlap Detection**: Prevents conflicting leave requests

- **Balance Validation**: Ensures sufficient leave balance

- **Policy Enforcement**: Applies company leave policies automatically



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



### System Administration



1. **Regular Audits**: Review leave data for accuracy

2. **Policy Updates**: Keep policies current with regulations

3. **Data Backup**: Regular backups of leave data

4. **Access Control**: Secure access to sensitive leave information



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

#### Approve Leave Request
**POST** `/api/leave/requests/{slug}/approve/`

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

#### Reject Leave Request
**POST** `/api/leave/requests/{slug}/reject/`

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
