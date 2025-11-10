"""
Utility views for the project app.

This module contains utility views for database backup, Excel import/export,
authentication methods, admin management, and token refresh functionality.
"""

import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import CustomUser, UserTenant
from accounts.audit import AuditLogger, get_client_ip

logger = logging.getLogger(__name__)


class BackupResponseSerializer(serializers.Serializer):
    """Serializer for backup database response"""
    message = serializers.CharField()
    backup_file = serializers.CharField()
    timestamp = serializers.DateTimeField()
    size = serializers.CharField()


@extend_schema(
    summary="Get available authentication methods",
    description="Returns available authentication methods including traditional and OAuth providers.",
    responses={
        200: {
            'description': 'Available authentication methods',
            'type': 'object',
            'properties': {
                'traditional': {
                    'type': 'object',
                    'properties': {
                        'endpoint': {'type': 'string'},
                        'method': {'type': 'string'},
                        'description': {'type': 'string'},
                        'fields': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                },
                'oauth': {
                    'type': 'object',
                    'properties': {
                        'providers': {
                            'type': 'object',
                            'properties': {
                                'google': {
                                    'type': 'object',
                                    'properties': {
                                        'login_url': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                },
                                'github': {
                                    'type': 'object',
                                    'properties': {
                                        'login_url': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_methods_view(request):
    """
    Returns available authentication methods
    """
    auth_methods = {
        'traditional': {
            'endpoint': '/api/login/',
            'method': 'POST',
            'description': 'Email and password authentication',
            'fields': ['email', 'password']
        },
        'oauth': {
            'providers': {
                'google': {
                    'login_url': '/accounts/google/login/',
                    'description': 'Login with Google account'
                },
                'github': {
                    'login_url': '/accounts/github/login/',
                    'description': 'Login with GitHub account'
                }
            }
        }
    }
    return Response(auth_methods)


@extend_schema(
    summary="Assign admin role to tenant member",
    description="Assign or remove admin (owner) role to/from an approved tenant member. Only current owners can perform this action.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID of user to assign/remove admin role'},
                'assign_admin': {'type': 'boolean', 'description': 'True to assign admin role, False to remove'}
            },
            'required': ['user_id', 'assign_admin']
        }
    },
    responses={
        200: {
            'description': 'Admin role assigned/removed successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user': {'type': 'string'},
                'role': {'type': 'string'},
                'is_owner': {'type': 'boolean'}
            }
        },
        400: {
            'description': 'Bad request - invalid user or assignment not allowed',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        403: {
            'description': 'Forbidden - only owners can assign admin roles',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        404: {
            'description': 'User not found',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_admin_view(request):
    """
    Assign or remove admin (owner) role to/from a tenant member.
    Only current owners can perform this action.
    """
    logger = logging.getLogger(__name__)

    # Get tenant from request
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
        UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'Only owners can assign admin roles'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    assign_admin = request.data.get('assign_admin')

    if user_id is None or assign_admin is None:
        return Response({'error': 'user_id and assign_admin are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get UserTenant relationship
    try:
        user_tenant = UserTenant.objects.get(user=target_user, tenant=tenant, is_approved=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'User is not an approved member of this tenant'}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent self-demotion if this would leave no owners
    if not assign_admin and user_tenant.is_owner:
        owner_count = UserTenant.objects.filter(tenant=tenant, is_owner=True).count()
        if owner_count <= 1:
            return Response({'error': 'Cannot remove admin role: tenant must have at least one owner'}, status=status.HTTP_400_BAD_REQUEST)

    # Update role
    user_tenant.is_owner = assign_admin
    user_tenant.role = 'Tenant Owner' if assign_admin else 'Employee'
    user_tenant.save()

    # Update user groups
    if assign_admin:
        # Add to Tenant Owners group
        try:
            owner_group = Group.objects.get(name='Tenant Owners')
            target_user.groups.add(owner_group)
        except Group.DoesNotExist:
            pass
    else:
        # Remove from Tenant Owners group, add to Employees
        try:
            owner_group = Group.objects.get(name='Tenant Owners')
            target_user.groups.remove(owner_group)
            employee_group = Group.objects.get(name='Employees')
            target_user.groups.add(employee_group)
        except Group.DoesNotExist:
            pass

    # Log admin assignment/removal
    try:
        AuditLogger.log(
            user=request.user,
            action='admin_assigned' if assign_admin else 'admin_removed',
            resource_type='user',
            resource_id=str(target_user.id),
            old_values={'is_owner': not assign_admin, 'role': 'Employee' if assign_admin else 'Tenant Owner'},
            new_values={'is_owner': assign_admin, 'role': user_tenant.role},
            ip_address=get_client_ip(request)
        )
    except Exception as e:
        logger.error(f"Failed to log admin assignment audit event: {e}")

    return Response({
        'message': f'Admin role {"assigned" if assign_admin else "removed"} successfully',
        'user': target_user.email,
        'role': user_tenant.role,
        'is_owner': user_tenant.is_owner
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Create database backup",
    description="Create a backup of the entire database and download it as JSON file.",
    responses={200: BackupResponseSerializer}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def backup_database_view(request):
    """
    Create a backup of the entire database and download it as JSON file.
    Only tenant owners can perform this action.
    """
    logger = logging.getLogger(__name__)

    # Get tenant from request
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
        UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'Only owners can create database backups'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.json'
        backup_path = os.path.join(settings.BASE_DIR, 'backend', backup_filename)

        # Create backup using Django's dumpdata command
        with open(backup_path, 'w') as f:
            call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)

        # Get file size
        file_size = os.path.getsize(backup_path)
        size_mb = file_size / (1024 * 1024)

        # Log backup creation
        try:
            AuditLogger.log(
                user=request.user,
                action='database_backup_created',
                resource_type='system',
                resource_id=backup_filename,
                metadata={
                    'backup_file': backup_filename,
                    'file_size': f"{size_mb:.2f} MB",
                    'created_at': timestamp
                },
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log database backup audit event: {e}")

        return Response({
            'message': 'Database backup created successfully',
            'backup_file': backup_filename,
            'created_at': timezone.now().isoformat(),
            'size': f"{size_mb:.2f} MB"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Database backup creation failed: {e}")
        return Response({'error': 'Failed to create database backup'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Export data to Excel",
    description="Export clients, projects, or tasks to Excel format",
    parameters=[
        OpenApiParameter(
            name='model',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Model to export (clients, projects, tasks)',
            required=True,
            enum=['clients', 'projects', 'tasks']
        )
    ],
    responses={
        200: {
            'description': 'Excel file download',
            'content': {
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                    'schema': {'type': 'string', 'format': 'binary'}
                }
            }
        },
        400: {
            'description': 'Invalid model type',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def excel_export_view(request):
    """
    Export data to Excel format. Supports clients, projects, and tasks.
    """
    logger = logging.getLogger(__name__)

    model_type = request.GET.get('model')
    if not model_type:
        return Response({'error': 'Model parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    if model_type not in ['clients', 'projects', 'tasks']:
        return Response({'error': 'Invalid model type. Must be one of: clients, projects, tasks'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        from .excel_utils import ClientExcelHandler, ProjectExcelHandler, TaskExcelHandler

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            # Check if user has any tenant association for security
            try:
                user_tenant = UserTenant.objects.filter(user=request.user, is_approved=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    return Response({'error': 'No tenant access found'}, status=status.HTTP_403_FORBIDDEN)
            except UserTenant.DoesNotExist:
                return Response({'error': 'No tenant access found'}, status=status.HTTP_403_FORBIDDEN)

        excel_data = None
        filename = ''

        if model_type == 'clients':
            handler = ClientExcelHandler(tenant)
            excel_data = handler.export_clients()
            filename = 'clients_export.xlsx'
        elif model_type == 'projects':
            handler = ProjectExcelHandler(tenant)
            excel_data = handler.export_projects()
            filename = 'projects_export.xlsx'
        elif model_type == 'tasks':
            handler = TaskExcelHandler(tenant)
            excel_data = handler.export_tasks()
            filename = 'tasks_export.xlsx'

        if not excel_data:
            return Response({'error': 'Invalid model type'}, status=status.HTTP_400_BAD_REQUEST)

        # Log export
        try:
            AuditLogger.log(
                user=request.user,
                action='data_exported',
                resource_type='excel_export',
                resource_id=model_type,
                metadata={'export_type': model_type},
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log data export audit event: {e}")

        # Return Excel file as response
        response = HttpResponse(
            excel_data.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        return Response({'error': 'Failed to export data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Import data from Excel",
    description="Import clients, projects, or tasks from Excel file",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Excel file to import'
                },
                'model': {
                    'type': 'string',
                    'enum': ['clients', 'projects', 'tasks'],
                    'description': 'Model type to import'
                }
            },
            'required': ['file', 'model']
        }
    },
    responses={
        200: {
            'description': 'Import completed',
            'type': 'object',
            'properties': {
                'imported': {'type': 'integer'},
                'updated': {'type': 'integer'},
                'errors': {'type': 'array', 'items': {'type': 'string'}},
                'warnings': {'type': 'array', 'items': {'type': 'string'}}
            }
        },
        400: {
            'description': 'Invalid request or file format',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def excel_import_view(request):
    """
    Import data from Excel file. Supports clients, projects, and tasks.
    """
    logger = logging.getLogger(__name__)

    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    model_type = request.POST.get('model')
    if not model_type:
        return Response({'error': 'Model parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    if model_type not in ['clients', 'projects', 'tasks']:
        return Response({'error': 'Invalid model type. Must be one of: clients, projects, tasks'},
                       status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']

    # Validate file type
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        return Response({'error': 'File must be an Excel file (.xlsx or .xls)'},
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        from .excel_utils import ClientExcelHandler, ProjectExcelHandler, TaskExcelHandler

        tenant = getattr(request, 'tenant', None)
        file_content = uploaded_file.read()

        if model_type == 'clients':
            handler = ClientExcelHandler(tenant)
            result = handler.import_clients(file_content)
        elif model_type == 'projects':
            handler = ProjectExcelHandler(tenant)
            result = handler.import_projects(file_content)
        elif model_type == 'tasks':
            handler = TaskExcelHandler(tenant)
            result = handler.import_tasks(file_content)

        # Log the import
        try:
            AuditLogger.log(
                user=request.user,
                action='data_imported',
                resource_type='excel_import',
                resource_id=model_type,
                metadata={
                    'import_type': model_type,
                    'imported_count': result.get('imported', 0),
                    'updated_count': result.get('updated', 0),
                    'errors_count': len(result.get('errors', []))
                },
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log data import audit event: {e}")

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Excel import failed: {e}")
        return Response({'error': 'Failed to import data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Refresh JWT access token",
    description="Refresh JWT access token using refresh token",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'JWT refresh token'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: {
            'description': 'Token refreshed successfully',
            'type': 'object',
            'properties': {
                'access': {'type': 'string'},
                'token_type': {'type': 'string'},
                'expires_in': {'type': 'integer'}
            }
        },
        401: {
            'description': 'Invalid or expired refresh token',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_view(request):
    """
    Refresh JWT access token using refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        from saasCRM.jwt_auth import JWTTokenManager
        
        access_token = JWTTokenManager.refresh_access_token(refresh_token)
        
        return Response({
            'access': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour
        }, status=status.HTTP_200_OK)
        
    except AuthenticationFailed as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return Response({'error': 'Token refresh failed'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)