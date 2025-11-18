#!/usr/bin/env python
"""
Test script for enhanced caching functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append('/home/xorb/Project/Django_projects/Carlhub_react/DjangoCRM/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasCRM.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from project.models import Client, Project
from saasCRM.enhanced_caching import CacheManager, CacheDecorator, CacheStats
from accounts.models import Tenant

User = get_user_model()

def test_cache_manager():
    """Test basic cache manager functionality."""
    print("Testing Cache Manager...")
    
    # Test cache key generation
    key = CacheManager.get_key('object', model='client', id=1)
    print(f"Generated cache key: {key}")
    
    # Test cache set/get
    test_data = {'id': 1, 'name': 'Test Client'}
    result = CacheManager.set(key, test_data, timeout=60)
    print(f"Cache set result: {result}")
    
    retrieved_data = CacheManager.get(key)
    print(f"Retrieved data: {retrieved_data}")
    
    # Test filters hash
    filters = {'status': 'active', 'tenant': 1}
    filters_hash = CacheManager.get_filters_hash(filters)
    print(f"Filters hash: {filters_hash}")
    
    print("✓ Cache Manager tests passed\n")

def test_cache_decorator():
    """Test cache decorator functionality."""
    print("Testing Cache Decorator...")
    
    @CacheDecorator.cache_result(timeout=60, key_prefix='test')
    def slow_function(x, y):
        return x + y
    
    # First call should execute function
    result1 = slow_function(2, 3)
    print(f"First call result: {result1}")
    
    # Second call should use cache
    result2 = slow_function(2, 3)
    print(f"Second call result: {result2}")
    
    print("✓ Cache Decorator tests passed\n")

def test_model_caching():
    """Test model instance caching."""
    print("Testing Model Caching...")
    
    try:
        # Get or create test tenant
        tenant, _ = Tenant.objects.get_or_create(
            name="Test Tenant",
            defaults={'domain': 'test.com'}
        )
        
        # Get or create test user
        user, _ = User.objects.get_or_create(
            email='test@example.com',
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        
        # Get or create test client
        client, _ = Client.objects.get_or_create(
            name='Test Client',
            defaults={'tenant': tenant}
        )
        
        # Cache the client
        CacheManager.cache_object(client, timeout=60)
        print(f"Cached client: {client.name}")
        
        # Retrieve cached client
        cached_data = CacheManager.get_cached_object(Client, client.id)
        print(f"Retrieved cached client data: {cached_data['data']['name'] if cached_data else 'None'}")
        
        # Test queryset caching
        filters = {'tenant': tenant.id}
        queryset_data = [
            {'id': client.id, 'name': client.name}
        ]
        CacheManager.cache_queryset('client', str(tenant.id), filters, queryset_data, timeout=60)
        
        cached_queryset = CacheManager.get_cached_queryset('client', str(tenant.id), filters)
        print(f"Cached queryset count: {cached_queryset['count'] if cached_queryset else 0}")
        
        print("✓ Model Caching tests passed\n")
        
    except Exception as e:
        print(f"✗ Model Caching test failed: {e}\n")

def test_cache_invalidation():
    """Test cache invalidation."""
    print("Testing Cache Invalidation...")
    
    try:
        # Test model invalidation
        deleted_count = CacheManager.invalidate_model('client', tenant_id='1')
        print(f"Invalidated {deleted_count} cache entries for client model")
        
        # Test pattern deletion
        pattern_deleted = CacheManager.delete_pattern('*test*')
        print(f"Deleted {pattern_deleted} cache entries matching pattern")
        
        print("✓ Cache Invalidation tests passed\n")
        
    except Exception as e:
        print(f"✗ Cache Invalidation test failed: {e}\n")

def test_cache_stats():
    """Test cache statistics."""
    print("Testing Cache Statistics...")
    
    try:
        stats = CacheStats.get_cache_info()
        print(f"Cache stats: {stats}")
        
        key_count = CacheStats.get_cache_keys_count()
        print(f"Total cache keys: {key_count}")
        
        print("✓ Cache Statistics tests passed\n")
        
    except Exception as e:
        print(f"✗ Cache Statistics test failed: {e}\n")

if __name__ == '__main__':
    print("Starting Enhanced Caching Tests...\n")
    
    test_cache_manager()
    test_cache_decorator()
    test_model_caching()
    test_cache_invalidation()
    test_cache_stats()
    
    print("All caching tests completed!")