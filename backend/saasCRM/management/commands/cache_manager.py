"""
Cache Management Command for DjangoCRM

This management command provides utilities for managing cache:
- Clear cache
- Show cache statistics
- Warm up cache with frequently accessed data
- Invalidate specific cache patterns
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from saasCRM.enhanced_caching import CacheManager, CacheStats
import time


class Command(BaseCommand):
    help = 'Manage DjangoCRM cache operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['clear', 'stats', 'warm', 'invalidate', 'info'],
            help='Action to perform'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Cache pattern to invalidate (used with invalidate action)'
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Model name to warm up cache for (used with warm action)'
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='Tenant ID to warm up cache for (used with warm action)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'clear':
            self.clear_cache()
        elif action == 'stats':
            self.show_stats()
        elif action == 'warm':
            self.warm_cache(options.get('model'), options.get('tenant_id'))
        elif action == 'invalidate':
            self.invalidate_pattern(options.get('pattern'))
        elif action == 'info':
            self.show_cache_info()

    def clear_cache(self):
        """Clear all cache."""
        try:
            from django.core.cache import cache
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('✓ Cache cleared successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error clearing cache: {e}')
            )

    def show_stats(self):
        """Show cache statistics."""
        self.stdout.write(self.style.TITLE('Cache Statistics'))
        
        stats = CacheStats.get_cache_info()
        
        if 'error' in stats:
            self.stdout.write(
                self.style.ERROR(f'✗ Error getting stats: {stats["error"]}')
            )
            return
        
        self.stdout.write(f"Redis Version: {stats.get('redis_version', 'N/A')}")
        self.stdout.write(f"Used Memory: {stats.get('used_memory', 'N/A')}")
        self.stdout.write(f"Connected Clients: {stats.get('connected_clients', 'N/A')}")
        self.stdout.write(f"Total Commands: {stats.get('total_commands_processed', 'N/A')}")
        self.stdout.write(f"Keyspace Hits: {stats.get('keyspace_hits', 0)}")
        self.stdout.write(f"Keyspace Misses: {stats.get('keyspace_misses', 0)}")
        self.stdout.write(f"Hit Rate: {stats.get('hit_rate', 0):.2f}%")
        
        # Count keys by pattern
        patterns = ['*client*', '*project*', '*task*', '*user*', '*tenant*']
        for pattern in patterns:
            count = CacheStats.get_cache_keys_count(pattern)
            self.stdout.write(f"Keys matching '{pattern}': {count}")

    def show_cache_info(self):
        """Show detailed cache configuration and status."""
        self.stdout.write(self.style.TITLE('Cache Configuration'))
        
        # Cache backend info
        cache_config = settings.CACHES.get('default', {})
        backend = cache_config.get('BACKEND', 'Not configured')
        location = cache_config.get('LOCATION', 'N/A')
        
        self.stdout.write(f"Backend: {backend}")
        self.stdout.write(f"Location: {location}")
        
        # Timeout configurations
        self.stdout.write(self.style.TITLE('Cache Timeouts'))
        for key, timeout in CacheManager.TIMEOUTS.items():
            self.stdout.write(f"{key}: {timeout}s ({timeout//60}m {timeout%60}s)")
        
        # Redis connection test
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            info = conn.info()
            self.stdout.write(self.style.SUCCESS('✓ Redis connection successful'))
            self.stdout.write(f"Redis Server: {info.get('redis_version')}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Redis connection failed: {e}')
            )

    def warm_cache(self, model=None, tenant_id=None):
        """Warm up cache with frequently accessed data."""
        self.stdout.write(self.style.TITLE('Warming Up Cache'))
        
        if not model:
            self.stdout.write(
                self.style.WARNING('Please specify --model to warm up cache for')
            )
            return
        
        try:
            # Import models dynamically
            if model == 'client':
                from project.models import Client
                queryset = Client.objects.all()
                if tenant_id:
                    queryset = queryset.filter(tenant_id=tenant_id)
                
                for client in queryset.select_related('tenant'):
                    CacheManager.cache_object(client)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Cached {queryset.count()} client objects'
                    )
                )
            
            elif model == 'project':
                from project.models import Project
                queryset = Project.objects.all()
                if tenant_id:
                    queryset = queryset.filter(tenant_id=tenant_id)
                
                for project in queryset.select_related('tenant', 'client'):
                    CacheManager.cache_object(project)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Cached {queryset.count()} project objects'
                    )
                )
            
            elif model == 'user':
                from accounts.models import CustomUser, UserTenant
                queryset = CustomUser.objects.all()
                
                for user in queryset.prefetch_related('usertenant_set'):
                    CacheManager.cache_object(user)
                    
                    # Cache user permissions for each tenant
                    for ut in user.usertenant_set.all():
                        # Mock permissions for demo
                        permissions = ['read', 'write']
                        CacheManager.cache_user_permissions(
                            user.id, ut.tenant_id, permissions
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Cached {queryset.count()} user objects and permissions'
                    )
                )
            
            else:
                self.stdout.write(
                    self.style.WARNING(f'Model "{model}" not supported for warming')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error warming cache: {e}')
            )

    def invalidate_pattern(self, pattern=None):
        """Invalidate cache keys matching pattern."""
        if not pattern:
            self.stdout.write(
                self.style.WARNING('Please specify --pattern to invalidate')
            )
            return
        
        start_time = time.time()
        deleted_count = CacheManager.delete_pattern(f"*{pattern}*")
        elapsed_time = time.time() - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Invalidated {deleted_count} cache keys matching "*{pattern}*" '
                f'in {elapsed_time:.3f}s'
            )
        )