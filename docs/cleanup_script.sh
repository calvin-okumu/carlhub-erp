#!/bin/bash
# DjangoCRM Documentation Monolithic-Era Cleanup Script
# Removes references to old backend/ directory, database users, and outdated patterns
# Focuses on current microservices architecture

set -e

echo "🧹 DjangoCRM Documentation Cleanup Script"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Phase 1: Backup Documentation${NC}"
echo ""

# Create backup directory
BACKUP_DIR="docs/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy all .md files to backup
cp docs/*.md docs/api/*.md docs/guides/*.md docs/overview/*.md docs/quick-start/*.md "$BACKUP_DIR/" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Documentation backed up to: $BACKUP_DIR${NC}"
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Phase 2: Removing Monolithic References${NC}"
echo ""

# Pattern 1: Remove cd backend commands (with variations)
echo -e "${YELLOW}Removing: cd backend commands...${NC}"
find docs -name "*.md" -type f -exec sed -i \
    -e 's/cd backend && python manage\.py runserver[[:space:]]*\.*/g' \
    -e 's/cd backend && python manage\.py runserver[[:space:]]*8000\.*/g' \
    -e 's/cd backend[^&]*$/g' \
    -e 's/cd backend[^/]*/g' \
    -e 's/cd backend[^|]*/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Removed cd backend commands${NC}"
else
    echo -e "${YELLOW}⚠  Some files may not have cd backend references${NC}"
fi

# Pattern 2: Replace saascrm_user with django_microservices
echo -e "${YELLOW}Updating database user references...${NC}"
find docs -name "*.md" -type f -exec sed -i \
    -e 's/saascrm_user/g' \
    -e 's/saascrm_password/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Updated database user references${NC}"
else
    echo -e "${YELLOW}⚠ Some files may not have saascrm_user references${NC}"
fi

# Pattern 3: Remove saascrm_db references
echo -e "${YELLOW}Removing monolithic database name...${NC}"
find docs -name "*.md" -type f -exec sed -i \
    -e 's/saascrm_db/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Removed monolithic database name${NC}"
else
    echo -e "${YELLOW}⚠ Some files may not have saascrm_db references${NC}"
fi

# Pattern 4: Update old endpoints to use /api/v1/ prefix
echo -e "${YELLOW}Updating API endpoint patterns...${NC}"

# Update login endpoint
find docs -name "*.md" -type f -exec sed -i \
    -e 's|http://localhost:8000/api/login/|g' \
    -e 's|http://localhost:8000/api/signup/|g' \
    -e 's|http://localhost:8000/api/invite-member/|g' \
    -e 's|http://localhost:8000/api/resend-invitation|g' \
    -e 's|http://localhost:8000/api/approve-member|g' \
    -e 's|http://localhost:8000/api/confirm-invitation|g' \
    2>/dev/null

# Update health endpoint
find docs -name "*.md" -type f -exec sed -i \
    -e 's|http://localhost:8000/api/health/|g' \
    's|http://localhost:8000/api/users/me|g' \
    2>/dev/null

# Update projects endpoint examples
find docs -name "*.md" -type f -exec sed -i \
    -e 's|http://localhost:8000/api/projects|g' \
    's|http://localhost:8000/api/projects/|g' \
    's|http://localhost:8000/api/clients|g' \
    -e 's|http://localhost:800:8000/api/tasks|g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Updated API endpoint patterns${NC}"
else
    echo -e "${YELLOW}⚠ Some endpoint patterns may remain${NC}"
fi

# Pattern 5: Remove docker-compose old format
echo -e "${YELLOW}Converting docker-compose to docker compose...${NC}"

find docs -name "*.md" -type f -exec sed -i \
    -e 's/docker-compose up/d/g' \
    -e 's/docker-compose down/g' \
    -e 's/docker-compose logs/g' \
    -e 's/docker-compose exec/g' \
    -e 's/docker-compose ps/g' \
    -e 's/docker-compose build/g' \
    -e 's/docker-compose restart/g' \
    -e 's/docker-compose -f docker-compose/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Converted docker-compose commands${NC}"
else
    echo -e "${YELLOW}⚠ Some docker-compose references may remain${NC}"
fi

# Pattern 6: Remove make dev commands
echo -e "${YELLOW}Removing make dev commands...${NC}"

find docs -name "*.md" -type f -exec sed -i \
    -e 's/make dev$/g' \
    -e 's/make dev-backend$/g' \
    -e 's/make dev-frontend$/g' \
    -e 's/make test-backend$/g' \
    -e 's/make test-frontend$/g' \
    -e 's/make env-check$/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Removed make dev commands${NC}"
else
    echo -e "${YELLOW}⚠ Some make commands may remain${NC}"
fi

# Pattern 7: Remove monolithic database setup commands
echo -e "${YELLOW}Removing monolithic database setup...${NC}"

find docs -name "*.md" -type f -exec sed -i \
    -e 's/sudo -u postgres createuser saascrm_user/dg' \
    -e 's/sudo -u postgres createdb saascrm_db -O saascrm_user/dg' \
    -e 's/sudo -u postgres psql -c "ALTER USER saascrm_user/dg' \
    -e 's/sudo -u postgres createdb saascrm_db -O saascrm_user$/g' \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Removed monolithic database setup commands${NC}"
else
    echo -e "${YELLOW}⚠ Some database commands may remain${NC}"
fi

echo ""
echo -e "${GREEN}Phase 3: Summary${NC}"
echo ""

# Count remaining monolithic references
REMAINING_BACKEND=$(grep -r "cd backend" docs/*.md 2>/dev/null | wc -l)
REMAINING_SAASCRM=$(grep -r "saascrm_user" docs/*.md 2>/dev/null | wc -l)
REMAINING_8000=$(grep -r "127.0.0.1:8000" docs/*.md 2>/dev/null | wc -l)
REMAINING_DOCKER_COMPOSE=$(grep -r "docker-compose " docs/*.md 2>/dev/null | wc -l)
REMAINING_MAKE_DEV=$(grep -r "make dev" docs/*.md 2>/dev/null | wc -l)

echo "Remaining monolithic references:"
echo "  - cd backend: $REMAINING_BACKEND"
echo "  - saascrm_user: $REMAINING_SAASCRM"
echo "  - 127.0.0.1:8000: $REMAINING_8000"
echo "  - docker-compose: $REMAINING_DOCKER_COMPOSE"
echo "  - make dev: $REMAINING_MAKE_DEV"

echo ""
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "Backup location: $BACKUP_DIR"
