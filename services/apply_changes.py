#!/usr/bin/env python3
"""
Script to add JWT tenant middleware and backup functionality to project-service
"""
import re

# Read current views.py
with open('services/project-service/project/views.py', 'r') as f:
    content = f.read()

# Add db_backup import
if 'from .db_backup import DatabaseBackup' not in content:
    # Find the line with permissions import
    import_section = re.search(
        r'(from .permissions import \[.*?\n)',
        content
    )
    if import_section:
        new_import = import_section.group(1) + "from .db_backup import DatabaseBackup\n"
        content = content.replace(import_section.group(0), new_import)

# Add BackupViewSet at end
backup_viewset = '''

class BackupViewSet(viewsets.ViewSet):
    """
    ViewSet for database backup operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_manager = DatabaseBackup('project-service')
    
    def list(self, request):
        """
        List all available backups
        """
        try:
            backups = self.backup_manager.list_backups()
            return Response({
                'backups': backups,
                'count': len(backups)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """
        Create a new database backup
        """
        try:
            backup_metadata = self.backup_manager.create_backup()
            return Response({
                'message': 'Backup created successfully',
                'backup': backup_metadata
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def restore(self, request):
        """
        Restore database from backup
        
        Args:
            backup_id: Timestamp ID of the backup to restore
        """
        backup_id = request.data.get('backup_id')
        
        if not backup_id:
            return Response(
                {'error': 'backup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.backup_manager.restore_backup(backup_id)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """
        Delete a backup
        """
        try:
            result = self.backup_manager.delete_backup(pk)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
'''

if not 'class BackupViewSet' in content:
    content += backup_viewset

# Write back
with open('services/project-service/project/views.py', 'w') as f:
    f.write(content)

print("✅ Added db_backup import and BackupViewSet to views.py")
