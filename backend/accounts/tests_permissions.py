from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import CustomPermission, PermissionGroup, Tenant, UserTenant

class PermissionManagementTestCase(APITestCase):
    def setUp(self):
        # Create test tenant and users
        self.tenant = Tenant.objects.create(name="Test Tenant", domain="test.com")
        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com", password="password"
        )
        self.regular_user = get_user_model().objects.create_user(
            email="user@test.com", password="password"
        )

        UserTenant.objects.create(
            user=self.admin_user, tenant=self.tenant, is_owner=True, is_approved=True
        )
        UserTenant.objects.create(
            user=self.regular_user, tenant=self.tenant, is_approved=True
        )

    def test_create_custom_permission(self):
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'name': 'Test Permission',
            'codename': 'test_permission',
            'description': 'A test permission',
            'category': 'custom'
        }

        response = self.client.post('/api/accounts/permissions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomPermission.objects.filter(codename='test_permission').exists())

    def test_create_permission_group(self):
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'name': 'Test Group',
            'description': 'A test permission group'
        }

        response = self.client.post('/api/accounts/permission-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PermissionGroup.objects.filter(name='Test Group', tenant=self.tenant).exists())

    def test_assign_permissions_to_group(self):
        self.client.force_authenticate(user=self.admin_user)

        # Create permission
        permission = CustomPermission.objects.create(
            name='Test Perm', codename='test_perm', category='custom'
        )

        # Create group
        group = PermissionGroup.objects.create(
            name='Test Group', tenant=self.tenant
        )

        # Assign permission
        response = self.client.post(
            f'/api/accounts/permission-groups/{group.id}/assign_permissions/',
            {'permission_ids': [str(permission.id)]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(permission, group.custom_permissions.all())

    def test_assign_users_to_group(self):
        self.client.force_authenticate(user=self.admin_user)

        # Create group
        group = PermissionGroup.objects.create(
            name='Test Group', tenant=self.tenant
        )

        # Assign user
        response = self.client.post(
            f'/api/accounts/permission-groups/{group.id}/assign_users/',
            {'user_ids': [self.regular_user.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.regular_user, group.users.all())

    def test_get_user_permissions(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(f'/api/accounts/users/{self.regular_user.id}/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('django_permissions', response.data)
        self.assertIn('custom_permissions', response.data)

    def test_permission_isolation_between_tenants(self):
        # Create another tenant
        other_tenant = Tenant.objects.create(name="Other Tenant", domain="other.com")
        other_admin = get_user_model().objects.create_user(
            email="other_admin@test.com", password="password"
        )
        UserTenant.objects.create(
            user=other_admin, tenant=other_tenant, is_owner=True, is_approved=True
        )

        # Create permission in other tenant
        other_permission = CustomPermission.objects.create(
            name='Other Permission', codename='other_perm', category='custom',
            created_by=other_admin, app_label=f"tenant_{other_tenant.id}"
        )

        # Admin from first tenant should not see other tenant's permission
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/accounts/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        if 'results' in data:
            permission_ids = [p['id'] for p in data['results']]
        else:
            permission_ids = [p['id'] for p in data]
        self.assertNotIn(str(other_permission.id), permission_ids)

    def test_non_admin_cannot_create_permissions(self):
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'name': 'Unauthorized Permission',
            'codename': 'unauthorized_perm',
            'category': 'custom'
        }

        response = self.client.post('/api/accounts/permissions/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomPermissionModelTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant", domain="test.com")
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password"
        )

    def test_permission_slug_generation(self):
        permission = CustomPermission.objects.create(
            name='Test Permission With Spaces',
            codename='test_perm_spaces',
            category='custom',
            created_by=self.user
        )
        self.assertEqual(permission.slug, 'test-permission-with-spaces')

    def test_permission_group_slug_generation(self):
        group = PermissionGroup.objects.create(
            name='Test Group With Spaces',
            tenant=self.tenant,
            created_by=self.user
        )
        self.assertEqual(group.slug, 'test-group-with-spaces')

    def test_unique_permission_codename(self):
        CustomPermission.objects.create(
            name='Test Perm 1', codename='test_perm', category='custom'
        )

        with self.assertRaises(Exception):
            CustomPermission.objects.create(
                name='Test Perm 2', codename='test_perm', category='custom'
            )

    def test_permission_group_unique_per_tenant(self):
        PermissionGroup.objects.create(
            name='Test Group', tenant=self.tenant
        )

        # Should allow same name in different tenant
        other_tenant = Tenant.objects.create(name="Other", domain="other.com")
        PermissionGroup.objects.create(
            name='Test Group', tenant=other_tenant
        )

        # Should not allow same name in same tenant
        with self.assertRaises(Exception):
            PermissionGroup.objects.create(
                name='Test Group', tenant=self.tenant
            )