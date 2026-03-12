# Tickets API

## Overview
The ticketing API supports inbound ticket creation from client systems and internal ticket management by agents/admins.

## Authentication
- Internal access: `Authorization: Token <token>`
- Inbound client access: `X-Client-Token: <api_key>`

## Endpoints

### List/Create tickets
`GET /api/tickets/`
`POST /api/tickets/`

Filters: `status`, `priority`, `assignee`, `client`, `created_at`

### Ticket detail
`GET /api/tickets/{id}/`
`PATCH /api/tickets/{id}/`
`DELETE /api/tickets/{id}/`

### Ticket comments
`GET /api/tickets/{id}/comments/`
`POST /api/tickets/{id}/comments/`

### Ticket attachments
`GET /api/tickets/{id}/attachments/`
`POST /api/tickets/{id}/attachments/`

### Ticket status history
`GET /api/tickets/{id}/status-history/`

### Inbound client ticket
`POST /api/tickets/inbound/`

Request body (standard payload)
```json
{
  "external_id": "ACME-1929",
  "client_slug": "acme-industries",
  "title": "VPN access failing",
  "description": "Users cannot authenticate after update.",
  "status": "open",
  "priority": "high",
  "category": "access",
  "requester_name": "John Smith",
  "requester_email": "john@acme.com",
  "attachments": [
    {
      "name": "error.log",
      "content_type": "text/plain",
      "content_base64": "..."
    }
  ]
}
```

Notes
- `external_id` must be unique per client to prevent duplicates.
- Alias support: `externalId` and `externalID` are accepted and normalized to `external_id`.
- Inbound requests are idempotent: if a ticket already exists for the `external_id`, the API returns `200 OK` with the existing ticket.
- When an inbound ticket already exists, the request is treated as a no-op (attachments are not re-created).
- Attachments are stored locally (MEDIA_ROOT).
- Attachments are validated and limited by `TICKETING_ATTACHMENT_MAX_BYTES` (default: 5 MB).
