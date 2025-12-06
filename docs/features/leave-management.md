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

- **Approval Levels**: Custom approval workflow for this leave type (max 5 levels)



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
5. **Approval/Rejection**: Manager approves or rejects with notes (approval details recorded in approval history)
6. **Balance Update**: Approved leave deducts from employee balance

7. **Notification**: All parties receive email notifications
    - **Approval Email**: Employee receives detailed approval confirmation with leave details
    - **Rejection Email**: Employee receives rejection notification with reason and next steps



### Automated Rules

- **Business Day Calculation**: Leave days exclude weekends
- **Overlap Detection**: Prevents conflicting leave requests
- **Balance Validation**: Ensures sufficient leave balance
- **Policy Enforcement**: Applies company leave policies automatically
- **Workflow Routing**: Automatic determination of approval workflow based on leave type and tenant defaults

## Email Notifications

DjangoCRM automatically sends professional email notifications for all leave request activities:

### Approval Notifications

**Trigger**: When a leave request is fully approved (all workflow levels completed)

**Recipient**: The employee who requested leave

**Content Includes**:
- Complete leave details (dates, type, duration, reason)
- Approver information and approval notes
- Updated leave balance information
- Next steps and reminders (update out-of-office, task handover)
- Link to view detailed leave information

### Rejection Notifications

**Trigger**: When a leave request is rejected at any workflow level

**Recipient**: The employee who requested leave

**Content Includes**:
- Complete leave details with rejection reason
- Approver information and rejection notes
- Guidance for resubmission or alternative arrangements
- Contact information for manager discussion
- Link to view leave request details

### Email Templates

- **leave_approved.html/txt**: Professional approval notification with green styling
- **leave_rejected.html/txt**: Clear rejection notification with red styling
- **Mobile-responsive**: All templates work on mobile devices
- **Consistent branding**: Matches site-wide email design standards

### Error Handling

- **Fail-safe**: Email failures don't prevent leave approval/rejection
- **Logging**: All email attempts are logged for debugging
- **Retry logic**: Automatic retry for temporary email service issues
- **Fallback**: Text-only versions ensure deliverability



## Leave Sales

DjangoCRM includes a comprehensive leave sales feature that allows employees to sell back unused leave days for cash compensation. This feature provides transparency, fair pricing control, and proper approval workflows.

### Key Features

- **Employee-Initiated Requests**: Employees can request to sell unused leave days
- **HR Pricing Control**: HR/admin sets fair pricing during approval process
- **Balance Validation**: Automatic validation of available leave days
- **Approval Workflow**: Configurable approval process for leave sales
- **Transaction Tracking**: Complete audit trail of all leave sales
- **Balance Updates**: Automatic deduction from leave balances upon completion

### Business Benefits

- **Employee Flexibility**: Employees can monetize unused leave days
- **Cost Control**: HR maintains control over pricing and approval
- **Financial Planning**: Predictable cash flow from leave sales
- **Compliance**: Transparent and auditable leave sale transactions
- **Employee Satisfaction**: Additional compensation option for unused leave

### Leave Sale Workflow

#### Employee Request
Employees submit leave sale requests specifying:

- Number of days to sell
- Optional leave type preference
- Reason for selling leave

**Request Validation:**
- Employee must have sufficient leave balance
- Days requested cannot exceed available balance
- System validates against current year's balance

#### HR Review and Pricing
HR/admin reviews requests and sets:

- Final leave type (can override employee preference)
- Sale price per day
- Approval decision

**Pricing Control:**
- HR has full control over pricing
- Can set different rates for different leave types
- Pricing is transparent and auditable

#### Approval Process
1. **Submission**: Employee creates sale request
2. **HR Review**: HR reviews and sets pricing
3. **Approval**: HR approves with pricing details
4. **Completion**: System deducts from leave balance
5. **Payment**: Employee receives compensation

#### Automated Rules

- **Balance Validation**: Ensures sufficient leave balance before approval
- **Pricing Calculation**: Automatic total calculation (days × price per day)
- **Balance Deduction**: Automatic update of leave balances upon completion
- **Audit Trail**: Complete record of all transactions

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

DjangoCRM supports configurable approval workflows that allow HR and tenant owners to define multi-level approval processes for leave requests. Workflows are configured as simple arrays of approval levels with a maximum of 5 levels per workflow.

### Key Features

- **Simple Configuration**: Configure approval levels as a JSON array (max 5 levels)
- **Role-Based Approvals**: Predefined roles: Department Manager, HR Manager, General Manager, Tenant Owner
- **Tenant-Scoped**: Workflows are configured per tenant
- **Default Fallback**: Automatic 1-level HR approval when no workflow is configured
- **Policy Integration**: Workflows can be linked to specific leave types via policies

### Available Approval Levels

- `"department_manager"` - Department Manager (employee's direct manager)
- `"hr_manager"` - HR Manager (any user with HR Manager role)
- `"general_manager"` - General Manager (any user with General Manager role)
- `"tenant_owner"` - Tenant Owner (any user with owner privileges)

### Default Behavior

When no workflow is configured, the system defaults to single-level HR approval:

1. **Default**: 1 level of HR Manager approval
2. **Fallback**: If no HR Manager exists, falls back to General Manager or Tenant Owner

### Workflow Configuration

HR configures workflows through the API by specifying approval levels in order:

#### Example: 3-Level Workflow
```json
{
  "name": "Standard 3-Level Approval",
  "description": "Department Manager → HR Manager → General Manager",
  "approval_levels": [
    "department_manager",
    "hr_manager",
    "general_manager"
  ],
  "default_hr_levels": 3,
  "is_default": true,
  "is_active": true
}
```

### Leave Sales

#### List Leave Sales
**GET** `/api/leave/sales/`

List leave sales with filtering and search.

**Query Parameters:**
- `status` - Filter by status (pending, approved, rejected, completed, cancelled)
- `leave_type` - Filter by leave type (annual_leave, sick_leave, etc.)
- `employee` - Filter by employee UUID

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "sale-uuid-annual-leave-5-2024-11-24",
      "employee": "uuid",
      "employee_name": "John Doe",
      "tenant": "uuid",
      "tenant_name": "Test Company",
      "leave_type": "annual_leave",
      "days_to_sell": "5.0",
      "sale_price_per_day": "25.00",
      "total_sale_amount": "125.00",
      "status": "approved",
      "approved_by": "uuid",
      "approved_by_name": "Jane Smith",
      "approved_date": "2024-11-24T10:00:00Z",
      "rejection_reason": "",
      "applied_date": "2024-11-24T09:00:00Z",
      "reason": "Need extra cash",
      "created_at": "2024-11-24T09:00:00Z",
      "updated_at": "2024-11-24T10:00:00Z"
    }
  ]
}
```

#### Create Leave Sale Request
**POST** `/api/leave/sales/`

Create a new leave sale request. Employees specify days to sell, HR sets pricing during approval.

**Request:**
```json
{
  "days_to_sell": 5,
  "leave_type": "annual_leave",
  "reason": "Selling unused annual leave days"
}
```

**Validation:**
- `days_to_sell` is required and must be positive
- Employee must have sufficient leave balance
- If `leave_type` specified, balance validation occurs immediately

**Response:**
```json
{
  "id": "uuid",
  "slug": "sale-uuid-annual-leave-5-2024-11-24",
  "employee": "uuid",
  "employee_name": "John Doe",
  "tenant": "uuid",
  "tenant_name": "Test Company",
  "leave_type": "annual_leave",
  "days_to_sell": "5.0",
  "sale_price_per_day": null,
  "total_sale_amount": "0.00",
  "status": "pending",
  "approved_by": null,
  "approved_date": null,
  "applied_date": "2024-11-24T09:00:00Z",
  "reason": "Selling unused annual leave days",
  "created_at": "2024-11-24T09:00:00Z",
  "updated_at": "2024-11-24T09:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: `["Insufficient leave balance. Available: 10.0 days, Requested to sell: 15.0 days."]`
- `400 Bad Request`: `["Number of days to sell is required."]`

#### Get Leave Sale
**GET** `/api/leave/sales/{slug}/`

Get detailed leave sale information.

#### Approve Leave Sale
**POST** `/api/leave/sales/{slug}/approve/`

HR approves a leave sale request and sets pricing. Only HR/admin can approve.

**Request:**
```json
{
  "action": "approve",
  "leave_type": "annual_leave",
  "days_to_sell": 5,
  "sale_price_per_day": 25.00,
  "notes": "Approved at $25 per day"
}
```

**Validation:**
- `sale_price_per_day` is required for approval
- `leave_type` and `days_to_sell` can be set/overridden by HR
- Sufficient leave balance is re-validated

**Response:**
```json
{
  "message": "Leave sale approved with details and pricing",
  "data": {
    "id": "uuid",
    "slug": "sale-uuid-annual-leave-5-2024-11-24",
    "leave_type": "annual_leave",
    "days_to_sell": "5.0",
    "sale_price_per_day": "25.00",
    "total_sale_amount": "125.00",
    "status": "approved",
    "approved_by": "uuid",
    "approved_by_name": "Jane Smith",
    "approved_date": "2024-11-24T10:00:00Z"
  }
}
```

#### Reject Leave Sale
**POST** `/api/leave/sales/{slug}/reject/`

HR rejects a leave sale request. Only HR/admin can reject.

**Request:**
```json
{
  "action": "reject",
  "notes": "Cannot approve at this time due to budget constraints"
}
```

**Response:**
```json
{
  "message": "Leave sale rejected",
  "data": {
    "status": "rejected",
    "rejection_reason": "Cannot approve at this time due to budget constraints"
  }
}
```

#### Complete Leave Sale
**POST** `/api/leave/sales/{slug}/complete/`

Complete an approved leave sale (deducts from leave balance). Can be called by HR/admin or automatically.

**Response:**
```json
{
  "message": "Leave sale completed",
  "data": {
    "status": "completed",
    "updated_at": "2024-11-24T11:00:00Z"
  }
}
```

#### Cancel Leave Sale
**POST** `/api/leave/sales/{slug}/cancel/`

Cancel a leave sale request. Only the employee who created it can cancel pending/approved requests.

**Response:**
```json
{
  "data": {
    "status": "cancelled",
    "updated_at": "2024-11-24T11:00:00Z"
  }
}
```

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
      "slug": "policy-uuid-annual-leave",
      "tenant": "uuid",
      "tenant_name": "Test Company",
      "leave_type": "annual_leave",
      "annual_entitlement": "25.0",
      "max_consecutive_days": 30,
      "notice_period_days": 7,
      "carry_over_allowed": true,
      "max_carry_over": null,
      "auto_approve_max_days": null,
      "approval_levels": [
        "department_manager",
        "hr_manager"
      ],
      "approval_workflow": null,
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
  "notice_period_days": 7,
  "approval_levels": [
    "department_manager",
    "hr_manager"
  ]
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
      "slug": "standard-3-level-approval",
      "name": "Standard 3-Level Approval",
      "description": "Department Manager → HR Manager → General Manager",
      "approval_levels": [
        "department_manager",
        "hr_manager",
        "general_manager"
      ],
      "approval_levels_display": "Department Manager → HR Manager → General Manager",
      "default_hr_levels": 3,
      "number_of_levels": 3,
      "is_default": true,
      "is_active": true,
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
  "name": "Standard 3-Level Approval",
  "description": "Department Manager → HR Manager → General Manager",
  "approval_levels": [
    "department_manager",
    "hr_manager",
    "general_manager"
  ],
  "default_hr_levels": 3,
  "is_default": true,
  "is_active": true
}
```

**Validation:**
- Maximum 5 levels per workflow
- Valid approval levels: `department_manager`, `hr_manager`, `general_manager`, `tenant_owner`
- At least 1 level required

**Response:** Same as list response format.

#### Get Workflow
**GET** `/api/leave/workflows/{slug}/`

Get detailed workflow information.

#### Update Workflow
**PUT/PATCH** `/api/leave/workflows/{slug}/`

Update workflow configuration.

#### Delete Workflow
**DELETE** `/api/leave/workflows/{slug}/`

Delete workflow (admin only).

#### Set Default Workflow
**POST** `/api/leave/workflows/{slug}/set_default/`

Set this workflow as the tenant default.

**Response:**
```json
{
  "message": "Workflow set as default",
  "workflow": {...}
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
**POST** `/api/leave/workflows/{slug}/quick_approve/`

Quick approve a leave request with minimal data (mobile-friendly).

#### Quick Reject Request
**POST** `/api/leave/workflows/{slug}/quick_reject/`

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
