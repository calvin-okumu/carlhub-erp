"""
Database Backup Utility for Microservices

Provides functions for creating, listing, restoring, and deleting database backups.
Stores backups locally with single backup retention policy.
"""
import os
import subprocess
import json
from datetime import datetime
from django.conf import settings


class DatabaseBackup:
    """
    Database backup manager for microservices
    """
    
    def __init__(self, service_name):
        """
        Initialize backup manager
        
        Args:
            service_name: Name of the service (e.g., 'project-service')
        """
        self.service_name = service_name
        self.db_name = os.getenv('DB_NAME', f'{service_name.replace("-service", "")}_db')
        self.db_user = os.getenv('DB_USER', 'django_microservices')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """
        Create a full database backup (schema + data)
        Overwrites previous backup (single backup retention policy)
        
        Returns:
            dict: Backup metadata
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'{self.db_name}_{timestamp}.sql.gz'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            env = {
                'PGPASSWORD': os.getenv('DB_PASSWORD', '')
            }
            
            cmd = [
                'pg_dump',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--username={self.db_user}',
                '--no-owner',
                '--no-privileges',
                '--format=plain',
                self.db_name
            ]
            
            with open(backup_path, 'wb') as backup_file:
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                gzip_process = subprocess.Popen(
                    ['gzip'],
                    stdin=process.stdout,
                    stdout=backup_file,
                    stderr=subprocess.PIPE
                )
                
                process.stdout.close()
                process.wait()
                gzip_process.wait()
                
                if process.returncode != 0:
                    raise Exception(f'pg_dump failed: {process.stderr.read().decode()}')
                if gzip_process.returncode != 0:
                    raise Exception(f'gzip failed: {gzip_process.stderr.read().decode()}')
            
            backup_size = os.path.getsize(backup_path)
            
            metadata = {
                'id': timestamp,
                'filename': backup_filename,
                'service_name': self.service_name,
                'database': self.db_name,
                'created_at': datetime.now().isoformat(),
                'size_bytes': backup_size,
                'size_human': self._format_size(backup_size),
                'path': backup_path
            }
            
            metadata_path = os.path.join(self.backup_dir, 'metadata.json')
            
            existing_metadata = []
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    existing_metadata = json.load(f)
            
            existing_metadata.append(metadata)
            
            with open(metadata_path, 'w') as f:
                json.dump(existing_metadata, f, indent=2)
            
            return metadata
            
        except Exception as e:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise Exception(f'Backup creation failed: {str(e)}')
    
    def list_backups(self):
        """
        List all available backups for this service
        
        Returns:
            list: List of backup metadata dicts
        """
        metadata_path = os.path.join(self.backup_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            return []
        
        with open(metadata_path, 'r') as f:
            all_backups = json.load(f)
        
        service_backups = [
            b for b in all_backups 
            if b.get('service_name') == self.service_name
        ]
        
        return sorted(service_backups, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def restore_backup(self, backup_id):
        """
        Restore database from backup
        
        Args:
            backup_id: Timestamp ID of the backup to restore
            
        Returns:
            dict: Restore result
        """
        backup_filename = f'{self.db_name}_{backup_id}.sql.gz'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            raise Exception(f'Backup file not found: {backup_filename}')
        
        try:
            env = {
                'PGPASSWORD': os.getenv('DB_PASSWORD', '')
            }
            
            with open(backup_path, 'rb') as backup_file:
                gunzip_process = subprocess.Popen(
                    ['gunzip', '-c', '-'],
                    stdin=backup_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                cmd = [
                    'psql',
                    f'--host={self.db_host}',
                    f'--port={self.db_port}',
                    f'--username={self.db_user}',
                    self.db_name
                ]
                
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdin=gunzip_process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                gunzip_process.stdout.close()
                process.wait()
                gunzip_process.wait()
                
                if gunzip_process.returncode != 0:
                    raise Exception(f'gunzip failed: {gunzip_process.stderr.read().decode()}')
                if process.returncode != 0:
                    raise Exception(f'psql failed: {process.stderr.read().decode()}')
            
            return {
                'success': True,
                'message': f'Database restored from backup {backup_id}',
                'backup_id': backup_id
            }
            
        except Exception as e:
            raise Exception(f'Restore failed: {str(e)}')
    
    def delete_backup(self, backup_id):
        """
        Delete a backup file
        
        Args:
            backup_id: Timestamp ID of the backup to delete
            
        Returns:
            dict: Delete result
        """
        backup_filename = f'{self.db_name}_{backup_id}.sql.gz'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            raise Exception(f'Backup file not found: {backup_filename}')
        
        try:
            os.remove(backup_path)
            
            metadata_path = os.path.join(self.backup_dir, 'metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    all_backups = json.load(f)
                
                all_backups = [
                    b for b in all_backups 
                    if not (b.get('service_name') == self.service_name and b.get('id') == backup_id)
                ]
                
                with open(metadata_path, 'w') as f:
                    json.dump(all_backups, f, indent=2)
            
            return {
                'success': True,
                'message': f'Backup {backup_id} deleted',
                'backup_id': backup_id
            }
            
        except Exception as e:
            raise Exception(f'Delete failed: {str(e)}')
    
    def _format_size(self, size_bytes):
        """
        Format file size in human-readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.2f} TB'
