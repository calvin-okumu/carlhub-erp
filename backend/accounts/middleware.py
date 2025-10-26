from django.utils.deprecation import MiddlewareMixin

from .audit import AuditLogger, get_client_ip, get_user_agent


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests for audit purposes.
    Captures user actions, IP addresses, and other relevant metadata.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view function.
        We capture the request details here for audit logging.
        """
        # Store request metadata for later use in audit logging
        request._audit_metadata = {
            'ip_address': get_client_ip(request),
            'user_agent': get_user_agent(request),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
        }

        # For POST/PUT/PATCH requests, store request body for audit logging
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Store a copy of the request body for audit logging
                # This is safe because Django's request body is read-once
                if hasattr(request, 'body') and request.body:
                    request._audit_request_body = request.body.decode('utf-8', errors='ignore')
            except Exception:
                # If we can't decode the body, just skip it
                request._audit_request_body = None

    def process_response(self, request, response):
        """
        Called just before Django returns the response.
        We log successful API calls here.
        """
        # Only log API requests (not admin, static files, etc.)
        if not request.path.startswith('/api/'):
            return response

        # Skip logging for certain endpoints that are too noisy
        skip_endpoints = [
            '/api/health/',
            '/api/auth-methods/',
            '/api/schema/',
        ]

        if any(request.path.startswith(endpoint) for endpoint in skip_endpoints):
            return response

        # Get user and tenant context
        user = getattr(request, 'user', None)
        tenant = getattr(request, 'tenant', None)

        # Only log authenticated requests or important unauthenticated ones
        if not user or not user.is_authenticated:
            # Log failed authentication attempts
            if request.path in ['/api/login/', '/api/signup/'] and response.status_code >= 400:
                AuditLogger.log_failed_login(
                    email=request.data.get('email') if hasattr(request, 'data') else 'unknown',
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request)
                )
            return response

        # Determine action type based on HTTP method and path
        action = self._determine_action(request, response)

        if action:
            metadata = getattr(request, '_audit_metadata', {})
            metadata.update({
                'status_code': response.status_code,
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
            })

            # Add request body for certain operations
            if hasattr(request, '_audit_request_body'):
                metadata['request_body'] = request._audit_request_body

            AuditLogger.log_event(
                action=action,
                resource_type=self._determine_resource_type(request),
                tenant=tenant,
                user=user,
                resource_id=self._extract_resource_id(request),
                ip_address=metadata.get('ip_address'),
                user_agent=metadata.get('user_agent'),
                metadata=metadata
            )

        return response

    def _determine_action(self, request, response) -> str:
        """Determine the audit action based on request method and path."""
        if response.status_code >= 400:
            # Error responses
            if request.method == 'POST' and '/login/' in request.path:
                return 'security_failed_login'
            return None  # Don't log all errors to avoid noise

        # Successful operations
        method = request.method
        path = request.path

        if '/signup/' in path and method == 'POST':
            return 'user_signup'
        elif '/login/' in path and method == 'POST':
            return 'user_login'
        elif '/logout/' in path and method == 'POST':
            return 'user_logout'
        elif '/invite-member/' in path and method == 'POST':
            return 'invitation_sent'
        elif '/approve-member/' in path and method == 'POST':
            return 'member_approved'
        elif '/invitations/' in path:
            if method == 'POST':
                return 'invitation_sent'
            elif method == 'DELETE':
                return 'invitation_cancelled'
        elif '/users/' in path or '/members/' in path:
            if method == 'POST':
                return 'user_created'
            elif method in ['PUT', 'PATCH']:
                return 'user_profile_update'
        elif '/projects/' in path:
            if method == 'POST':
                return 'project_created'
            elif method in ['PUT', 'PATCH']:
                return 'project_updated'
        elif '/tasks/' in path:
            if method == 'POST':
                return 'task_created'
            elif method in ['PUT', 'PATCH']:
                return 'task_updated'

        return None  # Don't log routine GET requests

    def _determine_resource_type(self, request) -> str:
        """Determine the resource type based on the request path."""
        path = request.path

        if '/users/' in path or '/members/' in path:
            return 'user'
        elif '/invitations/' in path or '/invite-member/' in path:
            return 'invitation'
        elif '/projects/' in path:
            return 'project'
        elif '/tasks/' in path:
            return 'task'
        elif '/clients/' in path:
            return 'client'
        elif '/tenants/' in path:
            return 'tenant'

        return 'unknown'

    def _extract_resource_id(self, request) -> str:
        """Extract resource ID from URL path."""
        # Try to extract from path for UUID-based URLs
        path_parts = request.path.strip('/').split('/')
        for part in reversed(path_parts):
            # Check if it looks like a UUID
            if len(part) == 36 and part.count('-') == 4:
                return part
            # Check if it looks like an integer ID
            if part.isdigit():
                return part

        return None


class AuditExceptionMiddleware(MiddlewareMixin):
    """
    Middleware to log exceptions for audit purposes.
    """

    def process_exception(self, request, response):
        """Log exceptions that occur during request processing."""
        user = getattr(request, 'user', None)
        tenant = getattr(request, 'tenant', None)

        if user and user.is_authenticated:
            AuditLogger.log_event(
                action='system_error',
                resource_type='system',
                tenant=tenant,
                user=user,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                metadata={
                    'error_path': request.path,
                    'error_method': request.method,
                    'exception_type': type(response).__name__ if response else 'Unknown',
                }
            )