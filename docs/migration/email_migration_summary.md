# Email Service Migration - Summary

## ✅ Completed

### 1. EmailService Copied
- `accounts/email_service.py` → `notification-service/notification/email_service.py`
- `accounts/email_service.py` → `identity-service/identity/email_service.py`
- `accounts/email_service.py` → `project-service/project/email_service.py`
- `accounts/email_service.py` → `hr-service/hr/email_service.py`

### 2. Email Templates Copied
- All 16 templates from `toremove/backend/templates/emails/` → `services/notification-service/templates/emails/`
  - invitation.html/txt
  - welcome.html/txt
  - password_reset.html/txt
  - leave_approved.html/txt
  - leave_rejected.html/txt
  - member_approved.html/txt
  - member_removed.html/txt
  - notification.html/txt
  - base.html

### 3. Email Settings Added
Updated settings.py in:
- ✅ `notification-service/notification_service/settings.py`
- ✅ `identity-service/identity_service/settings.py`
- ✅ `project-service/project_service/settings.py`
- ✅ `hr-service/hr_service/settings.py`

Added:
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- EMAIL_USE_TLS
- EMAIL_USE_SSL
- DEFAULT_FROM_EMAIL
- SITE_NAME
- FRONTEND_URL

### 4. Email Endpoints Added to Notification Service
- `/api/v1/email/send-invitation/` - Send team invitation email
- `/api/v1/email/send-welcome/` - Send welcome email
- `/api/v1/email/send-password-reset/` - Send password reset email
- `/api/v1/email/send-leave-approved/` - Send leave approval email
- `/api/v1/email/send-leave-rejected/` - Send leave rejection email
- `/api/v1/email/send-notification/` - Send general notification email

### 5. Email Integration Added to Services

#### Identity Service
- ✅ `password_reset` endpoint now sends actual email instead of stub
- ✅ Import EmailService and EmailError
- ✅ Send password reset email to user with reset URL

#### Project Service
- ✅ New `invite_team_member` action in ProjectViewSet
- ✅ Send invitation email with project details
- ✅ Generate invitation token and expiry

#### HR Service
- ✅ `approve` action now sends leave approval email
- ✅ `reject` action now sends leave rejection email
- ✅ Error handling with logging

## 📝 How to Use

### Configure Email (.env)
Add to each service's `.env` file:
```bash
# For development (console output)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For production (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@djangocrm.com
SITE_NAME=DjangoCRM
FRONTEND_URL=https://yourdomain.com
```

### Send Invitation Email (Project Service)
```bash
curl -X POST http://localhost:8006/api/v1/projects/invite_team_member/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "project_id": "project-uuid",
    "role": "team_member"
  }'
```

### Send Password Reset (Identity Service)
```bash
curl -X POST http://localhost:8001/api/v1/password_reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Send Leave Approval Email (HR Service)
```bash
curl -X POST http://localhost:8005/api/v1/leaves/{id}/approve/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Testing

### Console Email Backend (Development)
Emails will appear in console output when running services:
```bash
./start-local-services.sh
# View logs
tail -f services/logs/identity-service.log
```

### SMTP Email Backend (Production)
Configure real SMTP settings in .env files:
- Gmail: smtp.gmail.com:587 (use App Password)
- SendGrid: smtp.sendgrid.net:587
- AWS SES: email-smtp.us-east-1.amazonaws.com:587

## ✅ Result

**Email functionality is now fully integrated into microservices:**

1. ✅ User invitations send emails
2. ✅ Password reset sends actual emails
3. ✅ Leave approvals send notification emails
4. ✅ Leave rejections send notification emails
5. ✅ Welcome emails for new users
6. ✅ All email templates available

**API Endpoints Updated:**
- Identity Service: Password reset now works
- Project Service: Team member invitations now work
- HR Service: Leave notifications now send emails
- Notification Service: All email types available via API
