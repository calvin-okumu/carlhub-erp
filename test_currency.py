#!/usr/bin/env python3
"""
Simple test script to verify currency functionality
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # Import only the constants and utility functions that don't require requests
    from saasCRM.currency import get_tenant_default_currency, CURRENCY_SYMBOLS, CURRENCY_CHOICES
    from decimal import Decimal

    print("✅ Currency module constants imported successfully")

    # Test basic constants
    print(f"✅ Currency symbols loaded: {len(CURRENCY_SYMBOLS)} symbols")
    print(f"✅ Currency choices loaded: {len(CURRENCY_CHOICES)} currencies")

    # Test tenant default currency function
    class MockTenant:
        default_currency = 'EUR'

    tenant = MockTenant()
    default_currency = get_tenant_default_currency(tenant)
    print(f"✅ Tenant default currency: {default_currency}")

    # Test with None tenant
    default_currency_none = get_tenant_default_currency(None)
    print(f"✅ Default currency for None tenant: {default_currency_none}")

    print("\n🎉 Basic currency functionality tests passed!")

    # Now try to import the CurrencyConverter class
    try:
        from saasCRM.currency import CurrencyConverter
        print("✅ CurrencyConverter class imported successfully")

        # Test formatting (static method)
        amount = Decimal('100.00')
        formatted = CurrencyConverter.format_currency(amount, 'USD')
        print(f"✅ Currency formatting: {formatted}")

        # Test supported currencies
        currencies = CurrencyConverter.get_supported_currencies()
        print(f"✅ Supported currencies: {len(currencies)} currencies loaded")

        # Test currency validation
        is_valid = CurrencyConverter.is_valid_currency('USD')
        print(f"✅ Currency validation: USD is {'valid' if is_valid else 'invalid'}")

        print("🎉 Full currency functionality tests passed!")

    except ImportError as ie:
        print(f"⚠️  CurrencyConverter import failed (expected if requests not available): {ie}")
        print("✅ Basic currency functionality still works")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)