"""
Authentication views for the project app.

This module contains all authentication-related views including login, signup,
member approval, invitations, and user management functionality.
"""

import logging
import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.models import CustomUser, Invitation, Tenant, UserTenant
from accounts.audit import AuditLogger, get_client_ip
from accounts.email_service import EmailService, EmailError

logger = logging.getLogger(__name__)


@extend_schema(
    summary="User login",
    description="Authenticate user and return JWT tokens.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string'}
            },
            'required': ['email', 'password']
        }
    },
    responses={
        200: {
            'description': 'Login successful',
            'type': 'object',
            'properties': {
                'access': {'type': 'string'},
                'refresh': {'type': 'string'},
                'token_type': {'type': 'string'},
                'expires_in': {'type': 'integer'},
                'user_id': {'type': 'integer'},
                'email': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'message': {'type': 'string'}
            }
        },
        401: {
            'description': 'Invalid credentials',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    logger = logging.getLogger(__name__)
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            from saasCRM.jwt_auth import get_tokens_for_user
            
            tokens = get_tokens_for_user(user)

            # Log successful login (with error handling)
            try:
                tenant = None
                user_tenant = UserTenant.objects.filter(user=user, is_approved=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant

                AuditLogger.log_event(
                    action='user_login',
                    resource_type='user',
                    tenant=tenant,
                    user=user,
                    resource_id=str(user.id),
                    ip_address=get_client_ip(request),
                    metadata={'login_method': 'jwt'}
                )
            except Exception as e:
                logger.error(f"Failed to log login audit event: {e}")
                # Continue with login even if audit logging fails

            return Response({
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'token_type': 'Bearer',
                'expires_in': tokens['expires_in'],
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'message': 'Login successful'
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Login view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="User signup",
    description="Register a new user and optionally create a tenant. Supports invitation acceptance.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'minLength': 1},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'company_name': {'type': 'string'},
                'address': {'type': 'string'},
                'phone': {'type': 'string'},
                'website': {'type': 'string', 'format': 'uri'},
                'industry': {'type': 'string'},
                'company_size': {'type': 'string', 'enum': ['1-10', '11-50', '51-200', '201-1000', '1000+']},
                'invitation_token': {'type': 'string'}
            },
            'required': ['email', 'password', 'first_name', 'last_name']
        }
    },
    responses={
        200: {
            'description': 'Signup successful',
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'email': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'tenant': {'type': 'string'},
                'message': {'type': 'string'}
            }
        },
        400: {
            'description': 'Validation error',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_view(request):
    logger = logging.getLogger(__name__)
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        company_name = request.data.get('company_name')
        address = request.data.get('address', '')
        phone = request.data.get('phone', '')
        website = request.data.get('website', '')
        industry = request.data.get('industry', '')
        company_size = request.data.get('company_size', '')
        invitation_token = request.data.get('invitation_token')

        if not email or not password or not first_name or not last_name:
            return Response({'error': 'Email, password, first_name, and last_name are required'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        domain = email.split('@')[1]

        if invitation_token:
            try:
                invitation = Invitation.objects.get(token=invitation_token, is_used=False, expires_at__gt=timezone.now())
                if not invitation.email_confirmed:
                    return Response({'error': 'Please confirm your invitation by clicking the link in your email before signing up'}, status=status.HTTP_400_BAD_REQUEST)
                tenant = invitation.tenant
                role = invitation.role
                invitation.is_used = True
                invitation.save()
            except Invitation.DoesNotExist:
                return Response({'error': 'Invalid or expired invitation'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not company_name:
                return Response({'error': 'Company name required for new tenant'}, status=status.HTTP_400_BAD_REQUEST)
            if Tenant.objects.filter(domain=domain).exists():
                return Response({'error': 'Domain already in use'}, status=status.HTTP_400_BAD_REQUEST)

            # Basic validation for optional fields
            if website:
                validate = URLValidator()
                try:
                    validate(website)
                except ValidationError:
                    return Response({'error': 'Invalid website URL'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(email=email, password=password)

        if invitation_token:
            tenant = invitation.tenant
            role = invitation.role
        else:
            tenant = Tenant.objects.create(
                name=company_name,
                domain=domain,
                address=address,
                phone=phone,
                website=website,
                industry=industry,
                company_size=company_size,
                created_by=user
            )
            role = 'Tenant Owner'
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        # Approve users who are tenant owners OR have confirmed invitations
        is_approved = True if role == 'Tenant Owner' or invitation_token else False
        UserTenant.objects.create(user=user, tenant=tenant, is_owner=(role == 'Tenant Owner'), is_approved=is_approved, role=role)

        # Assign group only if approved
        if is_approved:
            group_name = {
                'Tenant Owner': 'Tenant Owners',
                'Employee': 'Employees',
                'Manager': 'Project Managers'
            }.get(role, 'Employees')

            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                # Fallback: create group if it doesn't exist (shouldn't happen with migration)
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

        token, _ = Token.objects.get_or_create(user=user)

        # Log successful signup (with error handling)
        try:
            AuditLogger.log_user_signup(
                user=user,
                tenant=tenant,
                invitation_used=invitation_token is not None,
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log signup audit event: {e}")
            # Continue with signup even if audit logging fails

        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tenant': tenant.name,
            'message': 'Signup successful'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Signup view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Approve tenant member",
    description="Approve a pending member request and assign appropriate group permissions.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'}
            },
            'required': ['user_id']
        }
    },
    responses={
        200: {
            'description': 'Member approved successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        },
        403: {
            'description': 'Permission denied',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_member_view(request):
    logger = logging.getLogger(__name__)
    try:
        if not hasattr(request, 'tenant') or not request.tenant:
            return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is owner
        try:
            user_tenant = UserTenant.objects.get(user=request.user, tenant=request.tenant, is_owner=True)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Only owners can approve members'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member_user_tenant = UserTenant.objects.get(user_id=user_id, tenant=request.tenant, is_owner=False, is_approved=False)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Pending member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if approving as owner and ensure minimum owners
        if member_user_tenant.role == 'Tenant Owner':
            # Count current owners
            current_owner_count = UserTenant.objects.filter(tenant=request.tenant, is_owner=True).count()
            if current_owner_count >= 1:  # Allow multiple owners but ensure at least one
                member_user_tenant.is_owner = True
                member_user_tenant.role = 'Tenant Owner'
            else:
                return Response({'error': 'Cannot approve member as owner: tenant must maintain at least one owner'}, status=status.HTTP_400_BAD_REQUEST)

        member_user_tenant.is_approved = True
        member_user_tenant.save()

        # Assign group based on role
        group_name = {
            'Tenant Owner': 'Tenant Owners',
            'Employee': 'Employees',
            'Manager': 'Project Managers'
        }.get(member_user_tenant.role, 'Employees')

        try:
            group = Group.objects.get(name=group_name)
            member_user_tenant.user.groups.add(group)
        except Group.DoesNotExist:
            # Fallback: create group if it doesn't exist (shouldn't happen with migration)
            group, created = Group.objects.get_or_create(name=group_name)
            member_user_tenant.user.groups.add(group)

        # Log member approval (with error handling)
        try:
            AuditLogger.log_member_approved(member_user_tenant, request.user, ip_address=get_client_ip(request))
        except Exception as e:
            logger.error(f"Failed to log member approval audit event: {e}")
            # Continue with approval even if audit logging fails

        return Response({'message': 'Member approved and added to group'})
    except Exception as e:
        logger.error(f"Approve member view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Invite member to tenant",
    description="Send an invitation email to join the tenant with specified role.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'role': {'type': 'string', 'enum': ['Employee', 'Manager', 'Tenant Owner']}
            },
            'required': ['email']
        }
    },
    responses={
        200: {
            'description': 'Invitation sent successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'token': {'type': 'string'}
            }
        },
        400: {
            'description': 'Bad request - user already a member or invalid data',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        403: {
            'description': 'Permission denied',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_member_view(request):
    logger = logging.getLogger(__name__)
    try:
        # Handle tenant context
        if hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
        else:
            # Dev mode: get tenant from user's ownership
            try:
                user_tenant = UserTenant.objects.get(user=request.user, is_owner=True)
                tenant = user_tenant.tenant
            except UserTenant.DoesNotExist:
                return Response({'error': 'No tenant ownership found'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is owner
        try:
            user_tenant = UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Only owners can invite members'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', 'Employee')

        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is already a member of this tenant
        if UserTenant.objects.filter(user__email=email, tenant=tenant).exists():
            return Response({'error': 'User is already a member of this tenant'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if there's already a pending invitation
        if Invitation.objects.filter(email=email, tenant=tenant, is_used=False).exists():
            return Response({'error': 'An invitation is already pending for this email in this tenant'}, status=status.HTTP_400_BAD_REQUEST)

        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)

        invitation = Invitation.objects.create(
            email=email,
            tenant=tenant,
            token=token,
            role=role,
            invited_by=request.user,
            expires_at=expires_at
        )

        # Log invitation creation (with error handling)
        try:
            AuditLogger.log_invitation_sent(invitation, ip_address=get_client_ip(request))
        except Exception as e:
            logger.error(f"Failed to log invitation sent audit event: {e}")
            # Continue with invitation even if audit logging fails

        # Send invitation email using EmailService
        try:
            EmailService.send_invitation_email(
                email=email,
                tenant=tenant,
                role=role,
                token=token,
                expires_at=expires_at,
                is_resend=False
            )
            return Response({'message': 'Invitation sent successfully', 'token': token})
        except EmailError as e:
            # Handle our custom email errors with enhanced information
            logger.error(f"Email service error for invitation to {email}: {e.category} - {str(e)}")

            return Response({
                'error': e.user_message,
                'error_category': e.category,
                'retryable': e.retryable
            }, status=e.status_code)
        except Exception as e:
            # Handle unexpected errors with fallback classification
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Unexpected error sending invitation email to {email}: {error_info['category']} - {str(e)}")

            return Response({
                'error': error_info['user_message'],
                'error_category': error_info['category'],
                'retryable': error_info['retryable']
            }, status=error_info['status_code'])
    except Exception as e:
        logger.error(f"Invite member view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Confirm invitation email",
    description="Confirm invitation email by marking the invitation as email_confirmed. This endpoint is called when a user clicks the confirmation link in their email.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'Invitation token'}
            },
            'required': ['token']
        }
    },
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Invitation token (for GET requests)'
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'invitation': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string'},
                        'tenant_name': {'type': 'string'},
                        'role': {'type': 'string'},
                        'expires_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def confirm_invitation_view(request):
    """
    Confirm invitation email by marking the invitation as email_confirmed.
    This endpoint is called when a user clicks the confirmation link in their email.
    Accepts both GET (for email links) and POST requests.
    """
    logger = logging.getLogger(__name__)
    try:
        if request.method == 'GET':
            token = request.GET.get('token')
        else:
            token = request.data.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(token=token, is_used=False, expires_at__gt=timezone.now())
        except Invitation.DoesNotExist:
            return Response({'error': 'Invalid or expired invitation token'}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.email_confirmed:
            return Response({'message': 'Invitation already confirmed', 'invitation': {
                'email': invitation.email,
                'tenant_name': invitation.tenant.name,
                'role': invitation.role
            }})

        invitation.email_confirmed = True
        invitation.save()

        # Log invitation confirmation (with error handling)
        try:
            AuditLogger.log_event(
                action='invitation_confirmed',
                resource_type='invitation',
                tenant=invitation.tenant,
                resource_id=str(invitation.slug),
                old_values={'email_confirmed': False},
                new_values={'email_confirmed': True},
                metadata={'confirmed_via': 'email_link'}
            )
        except Exception as e:
            logger.error(f"Failed to log invitation confirmation audit event: {e}")
            # Continue with confirmation even if audit logging fails

        return Response({
            'message': 'Invitation confirmed successfully',
            'invitation': {
                'email': invitation.email,
                'tenant_name': invitation.tenant.name,
                'role': invitation.role,
                'expires_at': invitation.expires_at
            }
        })
    except Exception as e:
        logger.error(f"Confirm invitation view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Resend invitation email",
    description="Resend invitation email for an existing invitation token. This allows users to request a new invitation email if they didn't receive the original.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'Invitation token'}
            },
            'required': ['token']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'invitation': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string'},
                        'tenant_name': {'type': 'string'},
                        'role': {'type': 'string'},
                        'expires_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        500: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_invitation_view(request):
    """
    Resend invitation email for an existing invitation token.
    This allows users to request a new invitation email if they didn't receive the original.
    """
    logger = logging.getLogger(__name__)
    try:
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(token=token, is_used=False, expires_at__gt=timezone.now())
        except Invitation.DoesNotExist:
            return Response({'error': 'Invalid or expired invitation token'}, status=status.HTTP_400_BAD_REQUEST)

        # Send invitation email using EmailService
        try:
            EmailService.send_invitation_email(
                email=invitation.email,
                tenant=invitation.tenant,
                role=invitation.role,
                token=token,
                expires_at=invitation.expires_at,
                is_resend=True
            )

            # Log invitation resend (with error handling)
            try:
                AuditLogger.log_event(
                    action='invitation_resent',
                    resource_type='invitation',
                    tenant=invitation.tenant,
                    resource_id=str(invitation.slug),
                    metadata={'resent_via': 'api_request'}
                )
            except Exception as e:
                logger.error(f"Failed to log invitation resend audit event: {e}")
                # Continue with resend even if audit logging fails

            return Response({
                'message': 'Invitation email resent successfully',
                'invitation': {
                    'email': invitation.email,
                    'tenant_name': invitation.tenant.name,
                    'role': invitation.role,
                    'expires_at': invitation.expires_at
                }
            })
        except EmailError as e:
            # Handle our custom email errors with enhanced information
            logger.error(f"Email service error resending invitation to {invitation.email}: {e.category} - {str(e)}")

            return Response({
                'error': e.user_message,
                'error_category': e.category,
                'retryable': e.retryable
            }, status=e.status_code)
        except Exception as e:
            # Handle unexpected errors with fallback classification
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Unexpected error resending invitation email to {invitation.email}: {error_info['category']} - {str(e)}")

            return Response({
                'error': error_info['user_message'],
                'error_category': error_info['category'],
                'retryable': error_info['retryable']
            }, status=error_info['status_code'])
    except Exception as e:
        logger.error(f"Resend invitation view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)