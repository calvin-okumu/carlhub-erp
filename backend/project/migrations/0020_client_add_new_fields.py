"""
Migration 0020: Actually add the new Client fields that migration 0019 declared
in state-only mode (SeparateDatabaseAndState with database_operations=[]).

This migration runs the real AddField operations so the columns exist in both
the ORM state and the database (including the SQLite in-memory test database).
"""

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_client_address_client_billing_address_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Apply real DDL to add the columns
            database_operations=[
                migrations.AddField(
                    model_name='client',
                    name='address',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='client',
                    name='billing_address',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='client',
                    name='company_size',
                    field=models.CharField(blank=True, default='', max_length=20),
                ),
                migrations.AddField(
                    model_name='client',
                    name='credit_limit',
                    field=models.DecimalField(
                        decimal_places=2,
                        default=Decimal('0.00'),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal('0'))],
                    ),
                ),
                migrations.AddField(
                    model_name='client',
                    name='industry',
                    field=models.CharField(blank=True, default='', max_length=100),
                ),
                migrations.AddField(
                    model_name='client',
                    name='lead_score',
                    field=models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                migrations.AddField(
                    model_name='client',
                    name='lead_source',
                    field=models.CharField(blank=True, default='', max_length=50),
                ),
                migrations.AddField(
                    model_name='client',
                    name='notes',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='client',
                    name='payment_terms',
                    field=models.CharField(blank=True, default='', max_length=50),
                ),
                migrations.AddField(
                    model_name='client',
                    name='tax_id',
                    field=models.CharField(blank=True, default='', max_length=50),
                ),
                migrations.AddField(
                    model_name='client',
                    name='website',
                    field=models.CharField(blank=True, default='', max_length=200),
                ),
            ],
            # State is already up-to-date from migration 0019
            state_operations=[],
        ),
    ]
