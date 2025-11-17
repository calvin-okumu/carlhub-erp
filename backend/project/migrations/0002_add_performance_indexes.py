# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        # Add indexes for Client model
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['tenant', 'status'], name='project_client_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['slug'], name='project_client_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['created_at'], name='project_client_created_at_idx'),
        ),
        
        # Add indexes for Project model
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['tenant', 'status'], name='project_project_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['client', 'created_at'], name='project_project_client_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['slug'], name='project_project_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['created_at'], name='project_project_created_at_idx'),
        ),
        
        # Add indexes for Milestone model
        migrations.AddIndex(
            model_name='milestone',
            index=models.Index(fields=['tenant', 'status'], name='project_milestone_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='milestone',
            index=models.Index(fields=['project', 'due_date'], name='project_milestone_project_due_date_idx'),
        ),
        migrations.AddIndex(
            model_name='milestone',
            index=models.Index(fields=['slug'], name='project_milestone_slug_idx'),
        ),
        
        # Add indexes for Sprint model
        migrations.AddIndex(
            model_name='sprint',
            index=models.Index(fields=['tenant', 'status'], name='project_sprint_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='sprint',
            index=models.Index(fields=['milestone', 'end_date'], name='project_sprint_milestone_end_date_idx'),
        ),
        migrations.AddIndex(
            model_name='sprint',
            index=models.Index(fields=['slug'], name='project_sprint_slug_idx'),
        ),
        
        # Add indexes for Task model
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['tenant', 'status'], name='project_task_tenant_status_idx'),
        ),
        # Note: Task doesn't have direct project field, it's accessed through milestone
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['milestone', 'status'], name='project_task_milestone_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['sprint', 'status'], name='project_task_sprint_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['assignee', 'status'], name='project_task_assignee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['slug'], name='project_task_slug_idx'),
        ),
        
        # Add indexes for Invoice model
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['tenant', 'paid'], name='project_invoice_tenant_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['client', 'issued_at'], name='project_invoice_client_issued_at_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['slug'], name='project_invoice_slug_idx'),
        ),
        
        # Add indexes for Payment model
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['tenant', 'paid_at'], name='project_payment_tenant_paid_at_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['invoice', 'paid_at'], name='project_payment_invoice_paid_at_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['slug'], name='project_payment_slug_idx'),
        ),
    ]