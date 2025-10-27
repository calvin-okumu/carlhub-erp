# Email System

DjangoCRM provides a comprehensive, professional email system with mobile-responsive HTML templates, centralized email handling, and extensive customization options.

## Overview

The email system is built around the `EmailService` class, which provides centralized email handling with consistent branding, error handling, and professional templates. All emails are sent with both HTML and text versions for maximum compatibility.

## Email Templates

### Base Template

All email templates extend from `backend/templates/emails/base.html`, which provides:

- **Responsive Design**: Mobile-first CSS with cross-browser compatibility
- **Consistent Branding**: Site-wide branding through context processors
- **Professional Styling**: Modern typography and spacing
- **Accessibility**: Proper contrast ratios and semantic HTML

### Available Templates

#### 1. Invitation Emails
**Files:** `invitation.html`, `invitation.txt`

Used for inviting new team members to join a tenant. Includes:
- Welcome message with tenant branding
- Step-by-step account creation instructions
- Email confirmation and signup links
- Expiration warnings and support contact

**Context Variables:**
- `email`: Recipient email address
- `tenant`: Tenant instance with name and branding
- `role`: User role (Employee, Manager, etc.)
- `confirmation_url`: Email verification link
- `signup_url`: Account creation link
- `expires_at`: Invitation expiration datetime
- `is_resend`: Boolean indicating if this is a resent invitation

#### 2. Welcome Emails
**Files:** `welcome.html`, `welcome.txt`

Sent automatically after successful user registration. Includes:
- Personalized welcome message
- Getting started guide
- Quick links to dashboard, profile, and help
- Security reminders

**Context Variables:**
- `user`: User instance with profile information
- `tenant`: Tenant instance
- `login_url`: Login page URL
- `profile_url`: Profile settings URL
- `dashboard_url`: Dashboard URL
- `help_url`: Help and support URL

#### 3. Password Reset Emails
**Files:** `password_reset.html`, `password_reset.txt`

Secure password recovery emails with expiration warnings. Includes:
- Password reset link with 24-hour expiration
- Security warnings and instructions
- Alternative link copying instructions
- Support contact information

**Context Variables:**
- `user`: User instance
- `reset_url`: Password reset link

#### 4. System Notification Emails
**Files:** `notification.html`, `notification.txt`

Flexible notification system for system events and alerts. Includes:
- Customizable title and message
- Optional action buttons and links
- Additional information sections
- Support contact details

**Context Variables:**
- `recipient`: User instance or email string
- `notification_title`: Email subject/title
- `notification_message`: Main notification content
- `notification_details`: Additional details (optional)
- `action_url`: Action button URL (optional)
- `action_text`: Action button text (optional)
- `additional_info`: Extra information (optional)

## Email Service API

### EmailService Class

Located in `backend/accounts/email_service.py`, provides static methods for all email operations with comprehensive error handling and configuration validation.

#### Error Handling

The EmailService includes robust error handling with intelligent error classification:

##### EmailError Exception

Custom exception class for email-related errors with enhanced information:

```python
class EmailError(Exception):
    def __init__(self, message, category='unknown', user_message=None, status_code=500, retryable=True):
        # category: authentication, connection, tls_ssl, rate_limit, mailbox, server_error, template_error
        # user_message: User-friendly error message
        # status_code: HTTP status code for API responses
        # retryable: Whether the operation can be retried
```

##### Error Classification

Automatic categorization of SMTP errors with appropriate user messages and status codes:

- **authentication**: SMTP login/credential failures
- **connection**: Network/SMTP server connectivity issues
- **tls_ssl**: Encryption/certificate problems
- **rate_limit**: Provider quota/throttling issues
- **mailbox**: Recipient delivery problems
- **server_error**: SMTP server internal errors
- **template_error**: Email template rendering failures

##### Configuration Validation

Pre-flight validation of email settings:

```python
validation = EmailService.validate_email_configuration()
# Returns: {'errors': [...], 'warnings': [...]}
```

Validates EMAIL_BACKEND, SMTP settings, Gmail App Password format, TLS/SSL configuration, and DEFAULT_FROM_EMAIL.

#### Methods

##### `validate_email_configuration()`

Validate email configuration and return detailed error/warning information.

**Returns:**
- `dict`: Dictionary with 'errors' and 'warnings' lists containing validation issues and solutions

##### `classify_email_error(error)`

Classify email errors and return appropriate user/admin messages.

**Parameters:**
- `error`: Exception object from email sending

**Returns:**
- `dict`: Error classification with user_message, admin_message, category, status_code, and retryable flag

##### `send_invitation_email(email, tenant, role, token, expires_at, is_resend=False)`

Send invitation email to new team members with comprehensive error handling.

**Parameters:**
- `email` (str): Recipient email address
- `tenant`: Tenant instance
- `role` (str): User role
- `token` (str): Invitation token
- `expires_at`: Expiration datetime
- `is_resend` (bool): Whether this is a resent invitation

**Raises:**
- `EmailError`: Enhanced error information for API responses

##### `send_welcome_email(user, tenant)`

Send welcome email to newly registered users (fail_silently=True).

**Parameters:**
- `user`: User instance
- `tenant`: Tenant instance

**Returns:**
- `bool`: Success status (used for logging, doesn't break signup on failure)

##### `send_password_reset_email(user, reset_url)`

Send password reset email (fail_silently=True).

**Parameters:**
- `user`: User instance
- `reset_url` (str): Password reset URL

**Returns:**
- `bool`: Success status (used for logging, doesn't break password reset on failure)

##### `send_notification_email(recipients, subject, message, tenant=None, **kwargs)`

Send customizable system notification emails with error handling.

**Parameters:**
- `recipients` (list): List of User instances or email strings
- `subject` (str): Email subject
- `message` (str): Main message content
- `tenant`: Optional tenant context
- `notification_details` (str): Additional details
- `action_url` (str): Action button URL
- `action_text` (str): Action button text
- `additional_info` (str): Extra information

**Returns:**
- `int`: Number of successfully sent emails

## Configuration

### Email Backend Settings

Configure email delivery in `backend/.env`:

```bash
# Development (console output)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Context Processors

Email templates automatically include site-wide context through `saasCRM.context_processors.email_context`:

- `site_name`: Site name (default: "DjangoCRM")
- `site_url`: Site URL from settings
- `support_email`: Support email from DEFAULT_FROM_EMAIL
- `current_year`: Current year for copyright notices

## Testing

### Template Testing

Run comprehensive template tests:

```bash
cd backend && python test_email_templates.py
```

This validates:
- All templates render without errors
- Required content is present
- HTML and text versions are consistent
- Context variables are properly substituted

### Email Delivery Testing

Test actual email delivery in development:

```bash
# Start server
cd backend && python manage.py runserver

# Test invitation in another terminal
curl -X POST http://localhost:8000/api/invite-member/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "role": "Employee"}'

# Check console output for email content
```

## Customization

### Template Customization

Modify templates in `backend/templates/emails/`:

1. **Base Template**: `base.html` - Update branding, colors, fonts
2. **Individual Templates**: Customize content and layout per email type
3. **Context Processors**: Add site-wide variables in `saasCRM/context_processors.py`

### Styling Guidelines

- **Mobile-First**: Design for mobile devices first
- **Consistent Colors**: Use CSS custom properties for theming
- **Accessibility**: Maintain WCAG contrast ratios
- **Cross-Browser**: Test in major email clients

### Adding New Templates

1. Create HTML and text template files
2. Add method to `EmailService` class
3. Update context processor if needed
4. Add tests to `test_email_templates.py`

## Best Practices

### Email Design
- Keep content concise and actionable
- Use clear subject lines and calls-to-action
- Include unsubscribe options for marketing emails
- Test in multiple email clients

### Security
- Never include sensitive information in emails
- Use secure, time-limited tokens
- Validate all email addresses
- Monitor for email delivery failures

### Performance
- Use background tasks for bulk email sending
- Implement rate limiting for email endpoints
- Cache template rendering when possible
- Monitor email delivery metrics

## Troubleshooting

### Common Issues

**Emails not sending:**
- Check EMAIL_BACKEND settings
- Verify SMTP credentials and configuration
- Run `EmailService.validate_email_configuration()` to check settings
- Review email-specific logs in `logs/backend/` directory
- Check for categorized error responses in API calls

**Configuration validation errors:**
- Run email configuration validation: `EmailService.validate_email_configuration()`
- Check for missing EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- Verify DEFAULT_FROM_EMAIL is set
- For Gmail: Ensure App Password is used (16 characters) instead of regular password

**Authentication failures:**
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Check if SMTP server requires App Passwords (Gmail, Outlook)
- Confirm EMAIL_HOST and EMAIL_PORT are correct
- Check firewall/network restrictions

**Connection issues:**
- Verify EMAIL_HOST is reachable
- Check EMAIL_PORT (587 for TLS, 465 for SSL, 25 for unencrypted)
- Confirm EMAIL_USE_TLS or EMAIL_USE_SSL is set appropriately
- Test network connectivity to SMTP server

**Templates not rendering:**
- Verify template file paths in `backend/templates/emails/`
- Check context variable names match template expectations
- Test with `test_email_templates.py`
- Check Django template syntax and debug template rendering
- Review template_error category in error responses

**Styling issues:**
- Test in email clients (Gmail, Outlook, Apple Mail, etc.)
- Use inline CSS for better compatibility
- Avoid complex CSS selectors and modern CSS features
- Test on mobile devices and various screen sizes

### Debug Mode

Enable comprehensive email logging for debugging:

```python
# Email-specific logging is configured in saasCRM/logging.py
# Logs are written to logs/backend/ directory with rotation

LOGGING = {
    'loggers': {
        'accounts.email_service': {
            'level': 'DEBUG',  # Detailed SMTP debugging
            'handlers': ['info_file', 'warning_file', 'error_file'],
        },
    }
}
```

**Log Files:**
- `logs/backend/info.log`: General email operations
- `logs/backend/warning.log`: Email warnings and configuration issues
- `logs/backend/error.log`: Email failures with categorized error information

**Debug Commands:**
```bash
# Test email configuration validation
python manage.py shell -c "from accounts.email_service import EmailService; print(EmailService.validate_email_configuration())"

# Test error classification
python manage.py shell -c "from accounts.email_service import EmailService; print(EmailService.classify_email_error(Exception('SMTP authentication failed')))"
```

## API Error Responses

Email-related API endpoints now provide enhanced error responses with categorized error information:

### Error Response Format

```json
{
  "error": "Email authentication failed. Please check your email credentials.",
  "error_category": "authentication",
  "retryable": false
}
```

**Error Categories:**
- `authentication`: SMTP credential issues
- `connection`: Network/SMTP connectivity problems
- `tls_ssl`: Security configuration issues
- `rate_limit`: Email provider limits exceeded
- `mailbox`: Recipient delivery problems
- `server_error`: Email service temporarily unavailable
- `template_error`: Email template rendering issues
- `unknown`: Unclassified errors

### Enhanced Endpoints

Email functionality integrates with these API endpoints with improved error handling:

- `POST /api/invite-member/` - Triggers invitation emails with categorized error responses
- `POST /api/signup/` - Triggers welcome emails (failures don't break signup)
- `POST /api/password-reset/` - Triggers password reset emails (failures don't break reset)
- `POST /api/resend-invitation/` - Resends invitation emails with enhanced error handling

### Signals and Hooks

Email sending can be extended through Django signals:

```python
from django.db.models.signals import post_save
from accounts.email_service import EmailService

def send_welcome_on_user_creation(sender, instance, created, **kwargs):
    if created:
        EmailService.send_welcome_email(instance, instance.tenant)

post_save.connect(send_welcome_on_user_creation, sender=User)
```

## Future Enhancements

### Recently Implemented
- ✅ **Enhanced Error Handling**: Comprehensive error classification and user-friendly messages
- ✅ **Configuration Validation**: Pre-flight email settings validation
- ✅ **Email-Specific Logging**: Detailed SMTP debugging and error tracking

### Planned Features
- **Email Analytics**: Delivery tracking and open rates
- **Template Editor**: Admin interface for template customization
- **Multi-language Support**: Localized email templates
- **Email Campaigns**: Marketing and newsletter functionality
- **Attachment Support**: File attachments for notifications
- **Email Health Checks**: API endpoint for email service monitoring
- **Retry Logic**: Automatic retry for temporary email failures