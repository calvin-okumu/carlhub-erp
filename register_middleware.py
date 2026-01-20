#!/usr/bin/env python3
"""
Register TenantFromJWTMiddleware in all service settings
"""
import os

services = [
    'identity-service',
    'audit-service',
    'notification-service',
    'accounting-service',
    'hr-service',
    'project-service',
    'sales-service'
]

for service in services:
    settings_file = f'services/{service}/{service.replace("-", "_")}_service/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"⚠️  Skipping {service} - settings file not found")
        continue
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    if 'TenantFromJWTMiddleware' in content:
        print(f"✅ {service}: TenantFromJWTMiddleware already registered")
        continue
    
    if "'django.middleware.security.SecurityMiddleware'," in content:
        insert_after = "'django.middleware.security.SecurityMiddleware',"
        middleware_line = f"    '{service.replace('-', '_')}.middleware.TenantFromJWTMiddleware',"
        
        content = content.replace(insert_after, insert_after + "\n" + middleware_line)
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print(f"✅ {service}: Registered TenantFromJWTMiddleware")
    else:
        print(f"⚠️  {service}: SecurityMiddleware line format different, manual update needed")

print("\n✅ Middleware registration complete")
