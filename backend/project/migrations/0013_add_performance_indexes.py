"""
Database Indexes Migration for DjangoCRM

This migration adds composite indexes for frequently queried combinations
to improve query performance.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_custompermission_accounts_cu_created_559aa4_idx'),
        ('project', '0012_alter_invoice_project_alter_milestone_project_and_more'),
    ]

    operations = [
        # Client indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_client_tenant_status ON project_client(tenant_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_client_tenant_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_client_tenant_name ON project_client(tenant_id, name);",
            reverse_sql="DROP INDEX IF EXISTS idx_client_tenant_name;"
        ),

        # Project indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_tenant_client ON project_project(tenant_id, client_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_tenant_client;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_tenant_status ON project_project(tenant_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_tenant_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_tenant_priority ON project_project(tenant_id, priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_tenant_priority;"
        ),

        # Milestone indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_milestone_tenant_project ON project_milestone(tenant_id, project_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_milestone_tenant_project;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_milestone_tenant_assignee ON project_milestone(tenant_id, assignee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_milestone_tenant_assignee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_milestone_project_status ON project_milestone(project_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_milestone_project_status;"
        ),

        # Sprint indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sprint_tenant_milestone ON project_sprint(tenant_id, milestone_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_sprint_tenant_milestone;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sprint_milestone_status ON project_sprint(milestone_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_sprint_milestone_status;"
        ),

        # Task indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_task_tenant_sprint ON project_task(tenant_id, sprint_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_task_tenant_sprint;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_task_tenant_assignee ON project_task(tenant_id, assignee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_task_tenant_assignee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_task_sprint_status ON project_task(sprint_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_task_sprint_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_task_assignee_status ON project_task(assignee_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_task_assignee_status;"
        ),

        # Invoice indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invoice_tenant_client ON project_invoice(tenant_id, client_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_invoice_tenant_client;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invoice_tenant_paid ON project_invoice(tenant_id, paid);",
            reverse_sql="DROP INDEX IF EXISTS idx_invoice_tenant_paid;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invoice_client_issued ON project_invoice(client_id, issued_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_invoice_client_issued;"
        ),

        # Payment indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_payment_tenant_invoice ON project_payment(tenant_id, invoice_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_payment_tenant_invoice;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_payment_invoice_paid ON project_payment(invoice_id, paid_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_payment_invoice_paid;"
        ),

        # UserTenant indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_usertenant_user_tenant ON accounts_usertenant(user_id, tenant_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_usertenant_user_tenant;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_usertenant_tenant_owner ON accounts_usertenant(tenant_id, is_owner);",
            reverse_sql="DROP INDEX IF EXISTS idx_usertenant_tenant_owner;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_usertenant_tenant_approved ON accounts_usertenant(tenant_id, is_approved);",
            reverse_sql="DROP INDEX IF EXISTS idx_usertenant_tenant_approved;"
        ),

        # Invitation indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invitation_tenant_email ON accounts_invitation(tenant_id, email);",
            reverse_sql="DROP INDEX IF EXISTS idx_invitation_tenant_email;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invitation_token_used ON accounts_invitation(token, is_used);",
            reverse_sql="DROP INDEX IF EXISTS idx_invitation_token_used;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invitation_expires ON accounts_invitation(expires_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_invitation_expires;"
        ),

        # AuditLog indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_auditlog_tenant_timestamp ON accounts_auditlog(tenant_id, timestamp);",
            reverse_sql="DROP INDEX IF EXISTS idx_auditlog_tenant_timestamp;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_auditlog_user_action ON accounts_auditlog(user_id, action);",
            reverse_sql="DROP INDEX IF EXISTS idx_auditlog_user_action;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_auditlog_resource ON accounts_auditlog(resource_type, resource_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_auditlog_resource;"
        ),

        # Custom indexes for complex queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_complex ON project_project(tenant_id, status, priority, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_complex;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_task_complex ON project_task(tenant_id, status, assignee_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_task_complex;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_milestone_complex ON project_milestone(tenant_id, status, project_id, due_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_milestone_complex;"
        ),
    ]
