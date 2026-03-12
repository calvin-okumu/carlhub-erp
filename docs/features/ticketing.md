# Ticketing

## Overview
The ticketing module provides end-to-end support request management for internal teams, with inbound integrations from client systems.

## Key Capabilities
- Inbound ticket creation via API key authentication
- Ticket lifecycle tracking with status history
- Client-linked tickets for reporting and analytics
- Local attachment storage for diagnostic files
- Internal agent assignment and prioritization

## Lifecycle
- `open` → `in_progress` → `resolved` → `closed`
- `blocked` supported for escalation or dependency issues

## Integrations
- Standard inbound payload with idempotency via `external_id`
- Per-client API keys for secure ingestion

### API Key Management
- Generate a key via management command:
  `python manage.py generate_client_api_key --client-slug <slug>`
- Rotate an existing key:
  `python manage.py generate_client_api_key --client-id <uuid> --rotate`
- Admin users can regenerate keys from the Client Integration admin action (key is shown once).

## Permissions
- Internal agents and admins manage tickets
- Tenant/client scoping enforced for isolation and analytics
