from .email_service import EmailService, EmailError

__all__ = ['EmailService', 'EmailError']


default_app_config = 'notification.apps.NotificationConfig'
