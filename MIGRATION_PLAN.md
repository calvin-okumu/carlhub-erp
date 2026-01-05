# Project Microservice Migration Plan

## Executive Summary
This plan migrates the project microservice to match all features from the monolithic backend (`toremove/backend/project/`).

**Status Gap:** 6,124 lines of code missing
- **Monolithic:** ~7,347 lines
- **Microservice:** ~1,223 lines
- **Missing:** ~6,124 lines (83% reduction)

---

## Phase 1: Authentication Fix (HIGH PRIORITY)
**Goal:** Fix JWT token generation bug to enable API testing

### Tasks
1. **Fix TypeError in identity-service**
   - File: `services/identity-service/venv/lib/python3.11/site-packages/rest_framework_simplejwt/tokens.py:173`
   - Issue: `datetime.datetime + int` operation
   - Fix: Ensure datetime operations use proper timedelta
   - Test: Login endpoint returns valid JWT token

**Deliverable:** Working authentication with JWT tokens

---

## Phase 2: Model Restoration (HIGH PRIORITY)
**Goal:** Restore all model fields and relationships

### 2a: Convert UUID ID Fields to ForeignKey Relationships
**Files:** `services/project-service/project/models.py`

**Changes Required:**
```python
# BEFORE (UUID fields)
tenant_id = models.UUIDField(db_index=True)
primary_contact_id = models.UUIDField(null=True, blank=True)
account_manager_id = models.UUIDField(null=True, blank=True)
assignee_id = models.UUIDField(null=True, blank=True)

# AFTER (ForeignKey relationships)
tenant = models.ForeignKey(
    "accounts.Tenant",
    on_delete=models.CASCADE,
    related_name="clients",
    null=True,
    blank=True,
    db_index=True,
)
primary_contact = models.ForeignKey(
    "accounts.CustomUser",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="primary_clients",
)
account_manager = models.ForeignKey(
    "accounts.CustomUser",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="managed_clients",
)
assignee = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="assigned_projects",
)
```

**Models to Update:**
- `Client` - tenant, primary_contact, account_manager
- `Contract` - tenant, client, project, approved_by, created_by
- `Project` - tenant, client, contract
- `Milestone` - tenant, project, assignee
- `Sprint` - tenant, milestone
- `Task` - tenant, milestone, sprint, assignee

### 2b: Add Missing Model Fields
**Missing Fields:**
1. **Project model:**
   - `team_members` = ManyToMany to settings.AUTH_USER_MODEL
   - `access_groups` = ManyToMany to Group

2. **Contract model:**
   - `contract_file` = FileField(upload_to="contracts/")
   - `signed_contract_file` = FileField(upload_to="contracts/signed/")

**Deliverable:** Complete models with all relationships

---

## Phase 3: Serializers (HIGH PRIORITY)
**Goal:** Add all missing serializers

### Tasks
1. **Copy from monolithic:** `toremove/backend/project/serializers.py`
2. **Adapt for microservice:** Update imports and relationships
3. **Add missing serializers:**
   - `TenantSerializer`
   - `CustomUserSerializer`
   - `UserTenantSerializer`
   - `InvitationSerializer`
   - `HealthCheckSerializer`

**File:** `services/project-service/project/serializers.py`

**Deliverable:** All serializers with proper validation

---

## Phase 4: Core Views (HIGH PRIORITY)
**Goal:** Add core ViewSets with mixins

### Tasks
1. **Copy mixins from monolithic:**
   - `OptimizedTenantScopedMixin`
   - `OptimizedViewSetMixin`

2. **Update existing ViewSets:**
   - `ClientViewSet` - Add mixins
   - `ProjectViewSet` - Add mixins
   - `MilestoneViewSet` - Add mixins
   - `SprintViewSet` - Add mixins
   - `TaskViewSet` - Add mixins
   - `ContractViewSet` - Add mixins

3. **File:** Create `services/project-service/project/views_core.py`

**Deliverable:** Core ViewSets with tenant scoping

---

## Phase 5: Authentication Views (HIGH PRIORITY)
**Goal:** Add authentication endpoints

### Tasks
1. **Copy from:** `toremove/backend/project/views_auth.py`
2. **Adapt views:**
   - `login_view(request)`
   - `signup_view(request)`
   - `approve_member_view(request)`

3. **File:** Create `services/project-service/project/views_auth.py`

**Deliverable:** Working authentication endpoints

---

## Phase 6: User Management Views (HIGH PRIORITY)
**Goal:** Add tenant/user/invitation management

### Tasks
1. **Copy from:** `toremove/backend/project/views_user_management.py`
2. **Add ViewSets:**
   - `TenantViewSet`
   - `UserTenantViewSet`
   - `UserViewSet`
   - `InvitationViewSet`

3. **File:** Create `services/project-service/project/views_user_management.py`

**Deliverable:** Complete user management API

---

## Phase 7: Utility Views (MEDIUM PRIORITY)
**Goal:** Add utility endpoints

### Tasks
1. **Copy from:** `toremove/backend/project/views_utils.py`
2. **Add views:**
   - `excel_export_view(request)`
   - `excel_import_view(request)`
   - `database_backup_view(request)`
   - `auth_methods_view(request)`
   - `assign_admin_view(request)`

3. **File:** Create `services/project-service/project/views_utils.py`

**Deliverable:** Utility API endpoints

---

## Phase 8: Permissions (MEDIUM PRIORITY)
**Goal:** Add comprehensive permission system

### Tasks
1. **Copy from:** `toremove/backend/project/permissions.py` (19,929 lines)
2. **Adapt for microservice:**
   - Update imports
   - Remove monolithic-specific code
   - Keep permission classes

3. **File:** `services/project-service/project/permissions.py`

**Deliverable:** Complete permission system

---

## Phase 9: Excel Utils (MEDIUM PRIORITY)
**Goal:** Add Excel export/import functionality

### Tasks
1. **Copy from:** `toremove/backend/project/excel_utils.py` (20,731 lines)
2. **Adapt for microservice:**
   - Update imports
   - Ensure model references are correct

3. **File:** `services/project-service/project/excel_utils.py`

**Deliverable:** Excel import/export capabilities

---

## Phase 10: Signals & Middleware (MEDIUM PRIORITY)
**Goal:** Add event-driven logic and middleware

### Tasks
1. **Copy signals.py:**
   - `toremove/backend/project/signals.py`
   - Adapt for microservice

2. **Copy middleware.py:**
   - `toremove/backend/project/middleware.py`
   - Adapt for microservice

**Deliverable:** Event handling and custom middleware

---

## Phase 11: Database Migrations (HIGH PRIORITY)
**Goal:** Create and apply migrations

### Tasks
1. **Generate migrations:**
   ```bash
   cd services/project-service
   python manage.py makemigrations
   ```

2. **Review migrations** for safety

3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

**Deliverable:** Database schema updated

---

## Phase 12: Testing (MEDIUM PRIORITY)
**Goal:** Ensure all features work

### Tasks
1. **Copy tests:** `toremove/backend/project/tests.py` (44,527 lines)
2. **Create tests for:**
   - All models
   - All serializers
   - All views
   - Permissions
   - Excel import/export

3. **Run tests:** `python manage.py test`

**Deliverable:** Comprehensive test suite

---

## Phase 13: Validation (HIGH PRIORITY)
**Goal:** End-to-end testing with authentication

### Tasks
1. **Test authentication flow:**
   - Login
   - Token refresh
   - Permission checks

2. **Test all endpoints:**
   - GET /api/v1/project/clients/
   - GET /api/v1/project/projects/
   - GET /api/v1/project/milestones/
   - GET /api/v1/project/tasks/
   - GET /api/v1/project/sprints/
   - GET /api/v1/project/contracts/

3. **Test utilities:**
   - Excel export/import
   - Database backup

**Deliverable:** All API endpoints working

---

## Execution Order

### Sprint 1 (Critical Path)
1. Phase 1: Authentication Fix
2. Phase 2a: ForeignKey Relationships
3. Phase 2b: Missing Model Fields
4. Phase 11: Database Migrations
5. Phase 13: Validation

### Sprint 2 (Core Features)
1. Phase 3: Serializers
2. Phase 4: Core Views
3. Phase 5: Auth Views
4. Phase 6: User Management Views

### Sprint 3 (Advanced Features)
1. Phase 8: Permissions
2. Phase 7: Utility Views
3. Phase 9: Excel Utils
4. Phase 10: Signals & Middleware
5. Phase 12: Testing

---

## Risk Assessment

### High Risk
- **Database migrations** - May break existing data
- **ForeignKey relationships** - May need to handle existing UUID data

### Medium Risk
- **Permissions system** - Complex logic may have bugs
- **Excel utils** - Large file (20k lines), complex to adapt

### Low Risk
- **Views** - Mostly code copy with minor adaptations
- **Serializers** - Straightforward migration

---

## Success Criteria

✅ All models match monolithic backend
✅ All ViewSets functional with tenant scoping
✅ Authentication working with JWT tokens
✅ All API endpoints tested and passing
✅ Excel import/export working
✅ Test suite passing
✅ No regressions in existing features

---

## Estimated Timeline

- **Sprint 1:** 2-3 days (Critical features)
- **Sprint 2:** 3-4 days (Core functionality)
- **Sprint 3:** 5-7 days (Advanced features)

**Total:** 10-14 days
