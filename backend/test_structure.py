#!/usr/bin/env python
"""
Test runner script to validate the enhanced testing structure.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasCRM.settings')
django.setup()

from django.test import TestCase
from rest_framework.test import APITestCase
from tests.utils import BaseTestCase, BaseAPITestCase, TestDataMixin
from accounts.factories import UserFactory, TenantFactory


def test_base_test_case():
    """Test BaseTestCase functionality."""
    print("Testing BaseTestCase...")
    
    class TestExample(BaseTestCase):
        def test_setup(self):
            self.assertIsNotNone(self.tenant)
            self.assertIsNotNone(self.user)
            self.assertIsNotNone(self.user_tenant)
            self.assertTrue(self.user_tenant.is_owner)
        
        def test_create_client(self):
            client = self.create_client()
            self.assertIsNotNone(client)
            self.assertEqual(client.tenant, self.tenant)
        
        def test_create_project(self):
            project = self.create_project()
            self.assertIsNotNone(project)
            self.assertEqual(project.tenant, self.tenant)
    
    # Run the test
    test_case = TestExample()
    test_case._pre_setup()
    test_case.setUp()
    
    try:
        test_case.test_setup()
        test_case.test_create_client()
        test_case.test_create_project()
        print("✓ BaseTestCase tests passed")
    except Exception as e:
        print(f"✗ BaseTestCase tests failed: {e}")
    finally:
        test_case._post_teardown()


def test_base_api_test_case():
    """Test BaseAPITestCase functionality."""
    print("Testing BaseAPITestCase...")
    
    class TestAPIExample(BaseAPITestCase):
        def test_setup(self):
            self.assertIsNotNone(self.tenant)
            self.assertIsNotNone(self.user)
            self.assertIsNotNone(self.user_tenant)
        
        def test_assertions(self):
            # Test assertion methods exist
            self.assertTrue(hasattr(self, 'assert_response_success'))
            self.assertTrue(hasattr(self, 'assert_response_created'))
            self.assertTrue(hasattr(self, 'assert_response_no_content'))
            self.assertTrue(hasattr(self, 'assert_response_bad_request'))
            self.assertTrue(hasattr(self, 'assert_response_unauthorized'))
            self.assertTrue(hasattr(self, 'assert_response_forbidden'))
            self.assertTrue(hasattr(self, 'assert_response_not_found'))
    
    # Run the test
    test_case = TestAPIExample()
    test_case._pre_setup()
    test_case.setUp()
    
    try:
        test_case.test_setup()
        test_case.test_assertions()
        print("✓ BaseAPITestCase tests passed")
    except Exception as e:
        print(f"✗ BaseAPITestCase tests failed: {e}")
    finally:
        test_case._post_teardown()


def test_data_mixin():
    """Test TestDataMixin functionality."""
    print("Testing TestDataMixin...")
    
    class TestDataExample(TestCase, TestDataMixin):
        pass
    
    test_case = TestDataExample()
    test_case._pre_setup()
    
    try:
        # Test static methods
        tenant = TestDataMixin.create_test_tenant()
        self.assertIsNotNone(tenant)
        
        user = TestDataMixin.create_test_user()
        self.assertIsNotNone(user)
        
        client = TestDataMixin.create_test_client(tenant=tenant)
        self.assertIsNotNone(client)
        self.assertEqual(client.tenant, tenant)
        
        project = TestDataMixin.create_test_project(tenant=tenant, client=client)
        self.assertIsNotNone(project)
        self.assertEqual(project.tenant, tenant)
        self.assertEqual(project.client, client)
        
        bulk_data = TestDataMixin.create_bulk_test_data(count=4)
        self.assertIsNotNone(bulk_data)
        self.assertIn('tenant', bulk_data)
        self.assertIn('clients', bulk_data)
        self.assertIn('projects', bulk_data)
        self.assertEqual(len(bulk_data['clients']), 2)
        self.assertEqual(len(bulk_data['projects']), 4)
        
        print("✓ TestDataMixin tests passed")
    except Exception as e:
        print(f"✗ TestDataMixin tests failed: {e}")
    finally:
        test_case._post_teardown()


def main():
    """Run all test structure validation tests."""
    print("Validating enhanced testing structure...")
    print("=" * 50)
    
    test_base_test_case()
    print()
    test_base_api_test_case()
    print()
    test_data_mixin()
    print()
    print("=" * 50)
    print("Testing structure validation complete!")


if __name__ == '__main__':
    main()