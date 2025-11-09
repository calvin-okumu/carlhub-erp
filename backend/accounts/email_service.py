"""
Email Service for DjangoCRM

Centralized email handling with customizable templates for professional communication.
Includes comprehensive error handling and configuration validation.
"""

import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """
    Custom exception for email-related errors with enhanced error information.
    """
    def __init__(self, message, category='unknown', user_message=None, status_code=500, retryable=True):
        super().__init__(message)
        self.category = category
        self.user_message = user_message or message
        self.status_code = status_code
        self.retryable = retryable


class EmailService:
    """
    Centralized email service for sending templated emails.

    Provides methods for different types of emails with consistent formatting
    and comprehensive error handling and configuration validation.
    """

    @staticmethod
    def validate_email_configuration():
        """
        Validate email configuration and return detailed error information.

        Returns:
            dict: Dictionary containing 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check EMAIL_BACKEND
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        if not backend:
            errors.append({
                'type': 'missing_backend',
                'message': 'EMAIL_BACKEND setting is not configured',
                'solution': 'Set EMAIL_BACKEND in your .env file',
                'severity': 'critical'
            })
        elif backend == 'django.core.mail.backends.console.EmailBackend':
            warnings.append({
                'type': 'console_backend',
                'message': 'Using console email backend - emails will only appear in console output',
                'solution': 'Configure SMTP backend for production email delivery',
                'severity': 'info'
            })

        # Check SMTP settings if using SMTP backend
        if 'smtp' in backend.lower():
            smtp_checks = [
                ('EMAIL_HOST', 'SMTP server hostname'),
                ('EMAIL_PORT', 'SMTP server port'),
                ('EMAIL_HOST_USER', 'SMTP username/email'),
                ('EMAIL_HOST_PASSWORD', 'SMTP password/App Password'),
            ]

            for setting_name, description in smtp_checks:
                value = getattr(settings, setting_name, '')
                if not value or str(value).strip() == '':
                    errors.append({
                        'type': 'missing_smtp_setting',
                        'setting': setting_name,
                        'message': f'{description} is required for SMTP but not configured',
                        'solution': f'Set {setting_name} in your .env file',
                        'severity': 'critical'
                    })

        # Check Gmail-specific configuration
        if getattr(settings, 'EMAIL_HOST', '').lower() == 'smtp.gmail.com':
            password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            if password and len(password) != 16:
                warnings.append({
                    'type': 'gmail_app_password_format',
                    'message': 'Gmail App Password should be 16 characters',
                    'solution': 'Verify you are using a Gmail App Password, not your regular password',
                    'severity': 'warning'
                })

        # Check TLS/SSL settings
        if 'smtp' in backend.lower():
            use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
            use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)

            if not use_tls and not use_ssl:
                warnings.append({
                    'type': 'no_encryption',
                    'message': 'Email connection is not encrypted (no TLS/SSL)',
                    'solution': 'Set EMAIL_USE_TLS=True for secure email transmission',
                    'severity': 'warning'
                })

        # Check DEFAULT_FROM_EMAIL
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        if not from_email:
            errors.append({
                'type': 'missing_from_email',
                'message': 'DEFAULT_FROM_EMAIL is not configured',
                'solution': 'Set DEFAULT_FROM_EMAIL in your .env file',
                'severity': 'high'
            })

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def classify_email_error(error):
        """
        Classify email errors and return appropriate user and admin messages.

        Args:
            error: Exception object from email sending

        Returns:
            dict: Error classification with user_message, admin_message, category, and status_code
        """
        error_str = str(error).lower()

        # SMTP Authentication errors
        if any(keyword in error_str for keyword in ['authentication', 'auth', 'login', 'credentials', '535', '534']):
            return {
                'category': 'authentication',
                'user_message': 'Email authentication failed. Please check your email credentials.',
                'admin_message': f'SMTP authentication failed - check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. Error: {error}',
                'status_code': 500,
                'retryable': False
            }

        # Connection errors
        elif any(keyword in error_str for keyword in ['connection', 'connect', 'network', 'timeout', '110', '111']):
            return {
                'category': 'connection',
                'user_message': 'Unable to connect to email service. Please try again later.',
                'admin_message': f'SMTP connection failed - check EMAIL_HOST and EMAIL_PORT. Error: {error}',
                'status_code': 503,
                'retryable': True
            }

        # TLS/SSL errors
        elif any(keyword in error_str for keyword in ['tls', 'ssl', 'certificate', 'handshake', '465', '587']):
            return {
                'category': 'tls_ssl',
                'user_message': 'Email security configuration issue. Please contact support.',
                'admin_message': f'TLS/SSL error - check EMAIL_USE_TLS and EMAIL_USE_SSL settings. Error: {error}',
                'status_code': 500,
                'retryable': False
            }

        # Rate limiting / quota exceeded
        elif any(keyword in error_str for keyword in ['rate', 'limit', 'quota', 'daily', '421', '450', '451']):
            return {
                'category': 'rate_limit',
                'user_message': 'Email sending limit reached. Please try again later.',
                'admin_message': f'Email provider rate limit exceeded. Error: {error}',
                'status_code': 429,
                'retryable': True
            }

        # Mailbox issues
        elif any(keyword in error_str for keyword in ['mailbox', 'recipient', '550', '551', '552', '553']):
            return {
                'category': 'mailbox',
                'user_message': 'Unable to deliver email to recipient. Please check the email address.',
                'admin_message': f'Mailbox delivery error. Error: {error}',
                'status_code': 400,
                'retryable': False
            }

        # Server errors
        elif any(keyword in error_str for keyword in ['server', 'internal', '500', '502', '503', '504']):
            return {
                'category': 'server_error',
                'user_message': 'Email service is temporarily unavailable. Please try again later.',
                'admin_message': f'Email server error. Error: {error}',
                'status_code': 503,
                'retryable': True
            }

        # Template rendering errors
        elif 'template' in error_str or 'render' in error_str:
            return {
                'category': 'template_error',
                'user_message': 'Email template error. Please contact support.',
                'admin_message': f'Email template rendering failed. Error: {error}',
                'status_code': 500,
                'retryable': False
            }

        # Default fallback for unknown errors
        else:
            return {
                'category': 'unknown',
                'user_message': 'Email service temporarily unavailable. Please try again later.',
                'admin_message': f'Unknown email error: {error}',
                'status_code': 500,
                'retryable': True
            }

    @staticmethod
    def send_invitation_email(email, tenant, role, token, expires_at, is_resend=False):
        """
        Send invitation email with customizable templates and comprehensive error handling.

        Args:
            email (str): Recipient email address
            tenant: Tenant instance
            role (str): User role (Employee, Manager, etc.)
            token (str): Invitation token
            expires_at: Expiration datetime
            is_resend (bool): Whether this is a resent invitation

        Raises:
            Exception: If email sending fails (with enhanced error information)
        """
        try:
            # Validate email configuration before attempting to send
            validation = EmailService.validate_email_configuration()
            if validation['errors']:
                error_msg = f"Email configuration invalid: {validation['errors'][0]['message']}"
                logger.error(f"Email configuration validation failed for invitation to {email}: {error_msg}")
                raise Exception(error_msg)

            context = {
                'email': email,
                'tenant': tenant,
                'role': role,
                'confirmation_url': f"{settings.FRONTEND_URL}{settings.FRONTEND_CONFIRMATION_PATH}/?token={token}",
                'signup_url': f"{settings.FRONTEND_URL}{settings.FRONTEND_SIGNUP_PATH}/?token={token}",
                'expires_at': expires_at,
                'is_resend': is_resend,
                'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                'site_url': settings.SITE_URL,
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            # Render templates with error handling
            try:
                html_content = render_to_string('emails/invitation.html', context)
                text_content = render_to_string('emails/invitation.txt', context)
            except Exception as template_error:
                logger.error(f"Template rendering failed for invitation email to {email}: {template_error}")
                raise Exception(f"Email template rendering failed: {template_error}")

            subject = f"Invitation to join {tenant.name}"
            if is_resend:
                subject += " (Resent)"

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")

            # Send email
            result = msg.send()
            if result == 0:
                logger.warning(f"Email send returned 0 recipients for invitation to {email}")
                raise Exception("Email was not sent to any recipients")
            elif result == 1:
                logger.info(f"Invitation email sent successfully to {email}")
            else:
                logger.info(f"Invitation email sent to {result} recipients")

            return result

        except Exception as e:
            # Classify and log the error
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Failed to send invitation email to {email} - Category: {error_info['category']}, Error: {str(e)}")

            # Re-raise with enhanced error information
            raise EmailError(
                message=error_info['admin_message'],
                category=error_info['category'],
                user_message=error_info['user_message'],
                status_code=error_info['status_code'],
                retryable=error_info['retryable']
            )

    @staticmethod
    def send_welcome_email(user, tenant):
        """
        Send welcome email to new users with error handling.

        Args:
            user: User instance
            tenant: Tenant instance

        Note: This method uses fail_silently=True to prevent signup failures
        """
        try:
            context = {
                'user': user,
                'tenant': tenant,
                'login_url': f"{settings.SITE_URL}/api/login/",
                'profile_url': f"{settings.SITE_URL}/api/profile/",
                'dashboard_url': f"{settings.SITE_URL}/api/dashboard/",
                'help_url': f"{settings.SITE_URL}/api/help/",
                'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            # Render templates with error handling
            try:
                html_content = render_to_string('emails/welcome.html', context)
                text_content = render_to_string('emails/welcome.txt', context)
            except Exception as template_error:
                logger.error(f"Template rendering failed for welcome email to {user.email}: {template_error}")
                return False  # Fail silently for welcome emails

            subject = f"Welcome to {tenant.name}!"

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")

            result = msg.send(fail_silently=True)
            if result > 0:
                logger.info(f"Welcome email sent successfully to {user.email}")
                return True
            else:
                logger.warning(f"Welcome email failed to send to {user.email}")
                return False

        except Exception as e:
            # Log error but don't raise - welcome emails shouldn't break signup
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Failed to send welcome email to {user.email} - Category: {error_info['category']}, Error: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Send password reset email with error handling.

        Args:
            user: User instance
            reset_url (str): Password reset URL

        Note: This method uses fail_silently=True to prevent password reset failures
        """
        try:
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            # Render templates with error handling
            try:
                html_content = render_to_string('emails/password_reset.html', context)
                text_content = render_to_string('emails/password_reset.txt', context)
            except Exception as template_error:
                logger.error(f"Template rendering failed for password reset email to {user.email}: {template_error}")
                return False  # Fail silently for password reset emails

            subject = f"Reset your {context['site_name']} password"

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")

            result = msg.send(fail_silently=True)
            if result > 0:
                logger.info(f"Password reset email sent successfully to {user.email}")
                return True
            else:
                logger.warning(f"Password reset email failed to send to {user.email}")
                return False

        except Exception as e:
            # Log error but don't raise - password reset emails shouldn't break the process
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Failed to send password reset email to {user.email} - Category: {error_info['category']}, Error: {str(e)}")
            return False

    @staticmethod
    def send_notification_email(recipients, subject, message, tenant=None, notification_details=None, action_url=None, action_text=None, additional_info=None):
        """
        Send notification emails for system events with error handling.

        Args:
            recipients (list): List of email addresses or User instances
            subject (str): Email subject
            message (str): Main notification message
            tenant: Optional tenant context
            notification_details (str): Additional details about the notification
            action_url (str): URL for action button
            action_text (str): Text for action button
            additional_info (str): Additional information to include

        Returns:
            int: Number of successfully sent emails
        """
        if not recipients:
            logger.warning("No recipients provided for notification email")
            return 0

        # Handle both email strings and User objects
        recipient_list = []
        for recipient in recipients:
            if hasattr(recipient, 'email'):
                recipient_list.append(recipient)
            else:
                # Assume it's an email string, create a mock recipient object
                recipient_list.append(type('MockRecipient', (), {'email': recipient, 'first_name': 'User'})())

        sent_count = 0
        errors = []

        for recipient in recipient_list:
            try:
                context = {
                    'recipient': recipient,
                    'notification_title': subject,
                    'notification_message': message,
                    'notification_details': notification_details,
                    'action_url': action_url,
                    'action_text': action_text,
                    'additional_info': additional_info,
                    'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                    'support_email': settings.DEFAULT_FROM_EMAIL,
                }

                # Render templates with error handling
                try:
                    html_content = render_to_string('emails/notification.html', context)
                    text_content = render_to_string('emails/notification.txt', context)
                except Exception as template_error:
                    logger.error(f"Template rendering failed for notification email to {recipient.email}: {template_error}")
                    errors.append(f"Template error for {recipient.email}: {template_error}")
                    continue

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.email]
                )
                msg.attach_alternative(html_content, "text/html")

                result = msg.send(fail_silently=True)
                if result > 0:
                    logger.info(f"Notification email sent successfully to {recipient.email}")
                    sent_count += 1
                else:
                    logger.warning(f"Notification email failed to send to {recipient.email}")
                    errors.append(f"Send failed for {recipient.email}")

            except Exception as e:
                error_info = EmailService.classify_email_error(e)
                logger.error(f"Failed to send notification email to {recipient.email} - Category: {error_info['category']}, Error: {str(e)}")
                errors.append(f"{recipient.email}: {error_info['category']}")

        if errors:
            logger.warning(f"Notification email completed with {len(errors)} errors: {errors}")

        return sent_count

    @staticmethod
    def send_leave_approved_email(leave_request):
        """
        Send email notification when a leave request is approved.

        Args:
            leave_request: LeaveRequest instance

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            context = {
                'leave_request': leave_request,
                'employee': leave_request.employee,
                'tenant': leave_request.tenant,
                'approver': leave_request.approved_by,
                'leave_details_url': f"{settings.SITE_URL}/api/leave/requests/{leave_request.id}/",
                'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            # Render templates with error handling
            try:
                html_content = render_to_string('emails/leave_approved.html', context)
                text_content = render_to_string('emails/leave_approved.txt', context)
            except Exception as template_error:
                logger.error(f"Template rendering failed for leave approved email to {leave_request.employee.email}: {template_error}")
                return False

            subject = f"Your leave request has been approved - {leave_request.tenant.name}"

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[leave_request.employee.email]
            )
            msg.attach_alternative(html_content, "text/html")

            result = msg.send(fail_silently=True)
            if result > 0:
                logger.info(f"Leave approved email sent successfully to {leave_request.employee.email}")
                return True
            else:
                logger.warning(f"Leave approved email failed to send to {leave_request.employee.email}")
                return False

        except Exception as e:
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Failed to send leave approved email to {leave_request.employee.email} - Category: {error_info['category']}, Error: {str(e)}")
            return False

    @staticmethod
    def send_leave_rejected_email(leave_request):
        """
        Send email notification when a leave request is rejected.

        Args:
            leave_request: LeaveRequest instance

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            context = {
                'leave_request': leave_request,
                'employee': leave_request.employee,
                'tenant': leave_request.tenant,
                'approver': leave_request.approved_by,
                'leave_details_url': f"{settings.SITE_URL}/api/leave/requests/{leave_request.id}/",
                'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            # Render templates with error handling
            try:
                html_content = render_to_string('emails/leave_rejected.html', context)
                text_content = render_to_string('emails/leave_rejected.txt', context)
            except Exception as template_error:
                logger.error(f"Template rendering failed for leave rejected email to {leave_request.employee.email}: {template_error}")
                return False

            subject = f"Your leave request has been rejected - {leave_request.tenant.name}"

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[leave_request.employee.email]
            )
            msg.attach_alternative(html_content, "text/html")

            result = msg.send(fail_silently=True)
            if result > 0:
                logger.info(f"Leave rejected email sent successfully to {leave_request.employee.email}")
                return True
            else:
                logger.warning(f"Leave rejected email failed to send to {leave_request.employee.email}")
                return False

        except Exception as e:
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Failed to send leave rejected email to {leave_request.employee.email} - Category: {error_info['category']}, Error: {str(e)}")
            return False