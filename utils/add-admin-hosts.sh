#!/bin/bash
# Script to add admin subdomain entries to /etc/hosts
# Run with: sudo bash utils/add-admin-hosts.sh

set -e

echo "=========================================="
echo "Adding Admin Subdomains to /etc/hosts"
echo "=========================================="

HOSTS_FILE="/etc/hosts"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    echo "   Run: sudo bash utils/add-admin-hosts.sh"
    exit 1
fi

# Backup existing hosts file
BACKUP_FILE="${HOSTS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$HOSTS_FILE" "$BACKUP_FILE"
echo "✅ Backed up $HOSTS_FILE to $BACKUP_FILE"

# Remove old admin subdomain entries if they exist
sed -i '/# DjangoCRM Admin Subdomains/,/# End DjangoCRM Admin/d' "$HOSTS_FILE"
echo "✅ Removed old admin subdomain entries (if any)"

# Add new admin subdomain entries
cat >> "$HOSTS_FILE" << 'EOF'

# DjangoCRM Admin Subdomains
127.0.0.1 admin.localhost
127.0.0.1 admin.identity.localhost
127.0.0.1 admin.audit.localhost
127.0.0.1 admin.notification.localhost
127.0.0.1 admin.accounting.localhost
127.0.0.1 admin.hr.localhost
127.0.0.1 admin.project.localhost
127.0.0.1 admin.sales.localhost
# End DjangoCRM Admin Subdomains
EOF

echo "✅ Added admin subdomain entries to $HOSTS_FILE"
echo ""
echo "=========================================="
echo "Admin Subdomains Added:"
echo "=========================================="
echo "  http://admin.localhost:8000/            → Redirects (not used directly)"
echo "  http://admin.identity.localhost:8000/  → Identity Admin"
echo "  http://admin.audit.localhost:8000/     → Audit Admin"
echo "  http://admin.notification.localhost:8000/ → Notification Admin"
echo "  http://admin.accounting.localhost:8000/ → Accounting Admin"
echo "  http://admin.hr.localhost:8000/        → HR Admin"
echo "  http://admin.project.localhost:8000/   → Project Admin"
echo "  http://admin.sales.localhost:8000/     → Sales Admin"
echo ""
echo "Next steps:"
echo "  1. Restart Traefik: ./restart-traefik.sh"
echo "  2. Test admin access in browser"
echo ""
