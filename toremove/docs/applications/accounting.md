# Accounting

The Accounting application handles all financial collection, billing, and payment processing within DjangoCRM.

## Overview

The Accounting app provides:

- **Invoice Management**: Create, send, and track invoices
- **Payment Processing**: Record and manage payments against invoices
- **Financial Reporting**: Revenue tracking and financial analytics
- **Multi-currency Support**: Handle transactions in different currencies
- **Audit Trail**: Complete financial transaction history

## Key Features

### Invoice Management
- **Invoice Creation**: Generate invoices from project milestones or custom billing
- **Invoice Numbering**: Automatic sequential numbering with custom prefixes
- **Status Tracking**: Draft → Sent → Paid workflow with overdue detection
- **Tax & Discounts**: Support for tax calculations and discount applications
- **PDF Generation**: Professional invoice templates (future feature)

### Payment Processing
- **Payment Recording**: Track payments against specific invoices
- **Payment Methods**: Support for bank transfers, cards, cash, checks, etc.
- **Partial Payments**: Handle partial payments on invoices
- **Currency Handling**: Automatic currency conversion and validation
- **Payment References**: Unique payment tracking numbers

### Financial Controls
- **Overdue Detection**: Automatic identification of overdue invoices
- **Payment Validation**: Prevent overpayments and invalid transactions
- **Audit Logging**: Complete transaction history for compliance
- **Tenant Isolation**: Financial data completely separated by tenant

## Architecture

### Data Models
- **Invoice**: Core billing document with status tracking
- **Payment**: Financial transaction records linked to invoices
- **Financial Reports**: Aggregated financial data and analytics

### API Endpoints
- `GET /api/accounting/invoices/` - List invoices
- `POST /api/accounting/invoices/` - Create invoice
- `GET /api/accounting/invoices/{id}/` - Get invoice details
- `PUT /api/accounting/invoices/{id}/` - Update invoice
- `POST /api/accounting/invoices/{id}/mark_as_paid/` - Mark invoice paid
- `POST /api/accounting/invoices/{id}/mark_as_sent/` - Mark invoice sent
- `GET /api/accounting/invoices/overdue/` - Get overdue invoices
- `GET /api/accounting/payments/` - List payments
- `POST /api/accounting/payments/` - Record payment
- `GET /api/accounting/invoices/summary/` - Invoice statistics
- `GET /api/accounting/payments/summary/` - Payment statistics

## Integration Points

### Sales App
- **Opportunity Conversion**: Sales opportunities can generate invoices
- **Client Data**: Shared client information for billing
- **Commission Tracking**: Future integration for sales commissions

### Project App
- **Milestone Billing**: Automatic invoice generation from project milestones
- **Time Tracking**: Billable hours integration
- **Project Budgets**: Financial tracking against project budgets

### CRM Core
- **Client Management**: Billing addresses and contact information
- **User Permissions**: Role-based access to financial data
- **Audit Logging**: Financial transaction compliance logging

## Security Features

### Data Protection
- **Tenant Isolation**: Complete financial data separation
- **Permission Controls**: Granular access to financial operations
- **Audit Trails**: All financial changes are logged

### Compliance
- **Transaction History**: Immutable financial records
- **Data Encryption**: Sensitive financial data protection
- **Access Logging**: Who accessed what financial data and when

## Business Workflows

### Invoice Lifecycle
```
Draft → Send to Client → Payment Received → Closed
   ↓         ↓                ↓
   → Cancelled  → Overdue → Collections
```

### Payment Processing
```
Invoice Generated → Payment Recorded → Funds Cleared → Reconciliation
```

## Future Enhancements

- **Automated Reminders**: Email notifications for overdue invoices
- **Payment Gateway Integration**: Direct payment processing
- **Recurring Billing**: Subscription and recurring invoice support
- **Multi-currency Conversion**: Real-time currency exchange
- **Financial Dashboards**: Advanced reporting and analytics
- **Tax Calculation**: Automated tax computation and reporting
- **Expense Management**: Track business expenses and reimbursements
