# Admin Subdomain Configuration

This document explains the admin subdomain setup for DjangoCRM microservices.

## Overview

Admin interfaces are accessible via subdomains for enhanced security:

```
http://admin.{service}.localhost:8000/
```

This provides:
- ✅ Browser cookie isolation per subdomain
- ✅ Stricter same-site policies
- ✅ CSRF token isolation
- ✅ Network-level access control (in production)
- ✅ Separate security policies per admin interface

## Access URLs

| Service | Admin URL | Direct URL (fallback) |
|---------|-----------|----------------------|
| Identity | http://admin.identity.localhost:8000/ | http://localhost:8001/admin/ |
| Audit | http://admin.audit.localhost:8000/ | http://localhost:8002/admin/ |
| Notification | http://admin.notification.localhost:8000/ | http://localhost:8003/admin/ |
| Accounting | http://admin.accounting.localhost:8000/ | http://localhost:8004/admin/ |
| HR | http://admin.hr.localhost:8000/ | http://localhost:8005/admin/ |
| Project | http://admin.project.localhost:8000/ | http://localhost:8006/admin/ |
| Sales | http://admin.sales.localhost:8000/ | http://localhost:8007/admin/ |

## Setup Instructions

### Step 1: Update /etc/hosts

Run the helper script:
```bash
sudo bash utils/add-admin-hosts.sh
```

Or manually add these entries to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1 admin.identity.localhost
127.0.0.1 admin.audit.localhost
127.0.0.1 admin.notification.localhost
127.0.0.1 admin.accounting.localhost
127.0.0.1 admin.hr.localhost
127.0.0.1 admin.project.localhost
127.0.0.1 admin.sales.localhost
```

### Step 2: Restart Traefik

```bash
./restart-traefik.sh
```

### Step 3: Verify Configuration

```bash
bash utils/verify-admin-access.sh
```

### Step 4: Access Admin Interfaces

Open your browser and navigate to:
- http://admin.project.localhost:8000/
- http://admin.identity.localhost:8000/
- etc.

## Troubleshooting

### Admin subdomain returns 404

**Problem**: `/etc/hosts` not updated
**Solution**: Run `sudo bash utils/add-admin-hosts.sh`

### Admin subdomain refuses connection

**Problem**: DNS resolution issue
**Solution**:
1. Check `/etc/hosts` contains the subdomain entries
2. Clear DNS cache: `sudo systemd-resolve --flush-caches` (Linux) or restart DNS service

### Can't login to admin

**Problem**: Admin requires Django superuser account
**Solution**: Create superuser in the respective service:
```bash
cd services/identity-service
python manage.py createsuperuser
```

### Redirect loops

**Problem**: Traefik or browser caching
**Solution**:
1. Restart Traefik: `./restart-traefik.sh`
2. Clear browser cookies for `*.localhost`

## Production Deployment

For production, replace `localhost` with your actual domain:

```toml
[http.routers.admin-identity]
  rule = "Host(`admin.identity.yourdomain.com`)"
  service = "identity"
  middlewares = ["admin-identity"]
```

### SSL Certificates

You'll need either:
1. **Wildcard certificate**: `*.yourdomain.com`
2. **Multiple certificates**: One per admin subdomain

### Firewall Rules

Restrict admin subdomains to internal network only:
```bash
# Allow admin subdomains from VPN/internal network only
# Block external access to admin.*.yourdomain.com
```

### Example Production Traefik Config

```toml
[http.routers.admin-identity]
  rule = "Host(`admin.identity.yourdomain.com`)"
  service = "identity"
  middlewares = ["admin-identity", "admin-auth", "admin-whitelist"]
  [http.routers.admin-identity.tls]
    certResolver = "letsencrypt"

[http.middlewares.admin-auth.basicAuth]
  users = ["admin:$apr1$encryptedpassword"]

[http.middlewares.admin-whitelist.ipWhiteList]
  sourceRange = ["10.0.0.0/8", "172.16.0.0/12"]
```

## Security Benefits

### Browser-Level Security

1. **Cookie Isolation**: Each admin subdomain has isolated cookies
2. **Same-Site Policies**: Stricter policies across subdomains
3. **CSRF Protection**: Tokens isolated per subdomain

### Network-Level Security (Production)

1. **Access Control**: Restrict admin subdomains to VPN/internal network
2. **Firewall Rules**: Block external access to admin subdomains
3. **Rate Limiting**: Apply stricter rate limits to admin subdomains

### Operational Security

1. **Audit Logging**: Separate access logs per admin subdomain
2. **Compartmentalization**: Compromise of one admin doesn't affect others
3. **Zero Trust**: Each admin subdomain can have unique authentication

## Comparison with Path-Based Access

| Feature | Path-Based (/admin/{service}) | Subdomain-Based (admin.{service}.localhost) |
|----------|------------------------------|------------------------------------------|
| Cookie Isolation | ❌ Same domain | ✅ Different origins |
| CSRF Protection | ⚠️  Shared tokens | ✅ Isolated tokens |
| Network Isolation | ❌ Same domain | ✅ Different domains |
| Production Security | ⚠️  Limited | ✅ Maximum |
| Implementation | ✅ Simple | ⚠️  Requires DNS/hosts |

## Next Steps

- [ ] Update `/etc/hosts` with admin subdomains
- [ ] Restart Traefik
- [ ] Run verification script
- [ ] Test admin access in browser
- [ ] Create superuser accounts in services
