"""
Email Service for DjangoCRM

Centralized email handling with customizable templates for professional communication.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class EmailService:
    """
    Centralized email service for sending templated emails.

    Provides methods for different types of emails with consistent formatting
    and error handling.
    """

    @staticmethod
    def send_invitation_email(email, tenant, role, token, expires_at, is_resend=False):
        """
        Send invitation email with customizable templates.

        Args:
            email (str): Recipient email address
            tenant: Tenant instance
            role (str): User role (Employee, Manager, etc.)
            token (str): Invitation token
            expires_at: Expiration datetime
            is_resend (bool): Whether this is a resent invitation

        Raises:
            Exception: If email sending fails
        """
        context = {
            'email': email,
            'tenant': tenant,
            'role': role,
            'confirmation_url': f"{settings.SITE_URL}/api/confirm-invitation/?token={token}",
            'signup_url': f"{settings.SITE_URL}/api/signup/?token={token}",
            'expires_at': expires_at,
            'is_resend': is_resend,
            'site_name': 'DjangoCRM',
            'site_url': settings.SITE_URL,
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }

        # Render HTML template
        html_content = render_to_string('emails/invitation.html', context)
        text_content = render_to_string('emails/invitation.txt', context)

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
        msg.send()

    @staticmethod
    def send_welcome_email(user, tenant):
        """
        Send welcome email to new users.

        Args:
            user: User instance
            tenant: Tenant instance
        """
        context = {
            'user': user,
            'tenant': tenant,
            'login_url': f"{settings.SITE_URL}/api/login/",
            'profile_url': f"{settings.SITE_URL}/api/profile/",
            'dashboard_url': f"{settings.SITE_URL}/api/dashboard/",
            'help_url': f"{settings.SITE_URL}/api/help/",
        }

        # Render HTML and text templates
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)

        subject = f"Welcome to {tenant.name}!"

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)  # Don't break signup if welcome email fails

    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Send password reset email.

        Args:
            user: User instance
            reset_url (str): Password reset URL
        """
        context = {
            'user': user,
            'reset_url': reset_url,
        }

        # Render HTML and text templates
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = render_to_string('emails/password_reset.txt', context)

        subject = f"Reset your {settings.SITE_NAME} password"

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)  # Don't break password reset if email fails

    @staticmethod
    def send_notification_email(recipients, subject, message, tenant=None, notification_details=None, action_url=None, action_text=None, additional_info=None):
        """
        Send notification emails for system events.

        Args:
            recipients (list): List of email addresses or User instances
            subject (str): Email subject
            message (str): Main notification message
            tenant: Optional tenant context
            notification_details (str): Additional details about the notification
            action_url (str): URL for action button
            action_text (str): Text for action button
            additional_info (str): Additional information to include
        """
        # Handle both email strings and User objects
        recipient_list = []
        for recipient in recipients:
            if hasattr(recipient, 'email'):
                recipient_list.append(recipient)
            else:
                # Assume it's an email string, create a mock recipient object
                recipient_list.append(type('MockRecipient', (), {'email': recipient, 'first_name': 'User'})())

        for recipient in recipient_list:
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

            # Render HTML and text templates
            html_content = render_to_string('emails/notification.html', context)
            text_content = render_to_string('emails/notification.txt', context)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)  # Don't break system if notification fails