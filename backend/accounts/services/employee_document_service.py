"""
Employee document service for handling document operations.
"""

from typing import Optional, Dict, Any, List
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import EmployeeDocument
from ..audit import AuditLogger, get_client_ip

User = get_user_model()


class EmployeeDocumentService:
    """Service for managing employee documents."""
    
    @staticmethod
    def get_user_documents(user: User) -> List[EmployeeDocument]:
        """Get all documents for a user."""
        return EmployeeDocument.objects.filter(user=user)
    
    @staticmethod
    def get_document(user: User, document_id: int) -> Optional[EmployeeDocument]:
        """Get a specific document for a user."""
        try:
            return EmployeeDocument.objects.get(id=document_id, user=user)
        except EmployeeDocument.DoesNotExist:
            return None
    
    @staticmethod
    def create_document(user: User, file_data: Dict[str, Any], 
                       title: str, request=None) -> EmployeeDocument:
        """Create a new employee document."""
        document = EmployeeDocument.objects.create(
            user=user,
            title=title,
            document_file=file_data['file'],
            file_type=file_data.get('file_type', ''),
            file_size=file_data.get('file_size', 0)
        )
        
        # Log document creation
        tenant = EmployeeDocumentService._get_user_tenant(user)
        if tenant:
            AuditLogger.log_event(
                action='document_created',
                resource_type='employee_document',
                tenant=tenant,
                user=user,
                resource_id=str(user.id),
                new_values={
                    'title': document.title,
                    'file_type': document.file_type,
                    'file_size': document.file_size
                },
                ip_address=get_client_ip(request) if request else None
            )
        
        return document
    
    @staticmethod
    def update_document(user: User, document_id: int, 
                       update_data: Dict[str, Any], request=None) -> EmployeeDocument:
        """Update an employee document."""
        document = EmployeeDocumentService.get_document(user, document_id)
        if not document:
            raise ValidationError("Document not found")
        
        # Store old values for audit
        old_data = {
            'title': document.title,
            'file_type': document.file_type,
            'file_size': document.file_size
        }
        
        # Update document
        if 'title' in update_data:
            document.title = update_data['title']
        if 'file' in update_data:
            document.document_file = update_data['file']
            document.file_type = update_data.get('file_type', document.file_type)
            document.file_size = update_data.get('file_size', document.file_size)
        document.save()
        
        # Get new values for audit
        new_data = {
            'title': document.title,
            'file_type': document.file_type,
            'file_size': document.file_size
        }
        
        # Log document update
        tenant = EmployeeDocumentService._get_user_tenant(user)
        if tenant:
            AuditLogger.log_event(
                action='document_updated',
                resource_type='employee_document',
                tenant=tenant,
                user=user,
                resource_id=str(user.id),
                old_values=old_data,
                new_values=new_data,
                ip_address=get_client_ip(request) if request else None
            )
        
        return document
    
    @staticmethod
    def delete_document(user: User, document_id: int, request=None) -> bool:
        """Delete an employee document."""
        document = EmployeeDocumentService.get_document(user, document_id)
        if not document:
            raise ValidationError("Document not found")
        
        # Store old values for audit
        old_data = {
            'title': document.title,
            'file_type': document.file_type,
            'file_size': document.file_size
        }
        
        # Log document deletion
        tenant = EmployeeDocumentService._get_user_tenant(user)
        if tenant:
            AuditLogger.log_event(
                action='document_deleted',
                resource_type='employee_document',
                tenant=tenant,
                user=user,
                resource_id=str(user.id),
                old_values=old_data,
                ip_address=get_client_ip(request) if request else None
            )
        
        document.delete()
        return True
    
    @staticmethod
    def can_access_document(user: User, document: EmployeeDocument) -> bool:
        """Check if user can access a document."""
        # Users can only access their own documents
        if document.user == user:
            return True
        
        # Superusers can access any document
        if user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def _get_user_tenant(user: User) -> Optional['Tenant']:
        """Get tenant context for a user."""
        try:
            user_tenant = user.usertenants.filter(is_approved=True).first()
            return user_tenant.tenant if user_tenant else None
        except:
            return None
    
    @staticmethod
    def get_document_stats(user: User) -> Dict[str, Any]:
        """Get document statistics for a user."""
        documents = EmployeeDocumentService.get_user_documents(user)
        
        total_size = sum(doc.file_size or 0 for doc in documents)
        file_types = {}
        
        for doc in documents:
            file_type = doc.file_type or 'unknown'
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_documents': len(documents),
            'total_size': total_size,
            'file_types': file_types,
            'recent_documents': sorted(documents, key=lambda x: x.uploaded_at, reverse=True)[:5]
        }