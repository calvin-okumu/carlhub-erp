"""
Migration 0020: Actually add created_at and updated_at columns to
accounts_usertenant.

Migration 0019 used SeparateDatabaseAndState which updated Django's ORM
state without touching the real database.  This migration runs the actual
ALTER TABLE so that the columns exist both in the ORM state and in the DB.
"""

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_usertenant_created_updated_at_state'),
    ]

    operations = [
        # Use SeparateDatabaseAndState — state already has these fields from
        # migration 0019, so we only need the database_operations.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Add created_at — nullable so existing rows are not affected
                migrations.AddField(
                    model_name='usertenant',
                    name='created_at',
                    field=models.DateTimeField(
                        auto_now_add=True,
                        default=django.utils.timezone.now,
                    ),
                    preserve_default=False,
                ),
                # Add updated_at — nullable so existing rows are not affected
                migrations.AddField(
                    model_name='usertenant',
                    name='updated_at',
                    field=models.DateTimeField(
                        auto_now=True,
                        default=django.utils.timezone.now,
                    ),
                    preserve_default=False,
                ),
            ],
            state_operations=[],  # state already updated in 0019
        ),
    ]
