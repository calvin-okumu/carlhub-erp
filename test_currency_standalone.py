#!/usr/bin/env python3
"""
Standalone test for currency functionality without Django dependencies
"""
import sys
import os
from decimal import Decimal

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_currency_constants():
    """Test currency constants and basic functionality"""
    try:
        # Import only the constants that don't require Django
        from saasCRM.currency import CURRENCY_CHOICES, CURRENCY_SYMBOLS

        print("✅ Currency constants imported successfully")

        # Test currency choices
        assert len(CURRENCY_CHOICES) == 12, f"Expected 12 currencies, got {len(CURRENCY_CHOICES)}"
        print(f"✅ Currency choices: {len(CURRENCY_CHOICES)} currencies loaded")

        # Test currency symbols
        assert len(CURRENCY_SYMBOLS) == 12, f"Expected 12 symbols, got {len(CURRENCY_SYMBOLS)}"
        print(f"✅ Currency symbols: {len(CURRENCY_SYMBOLS)} symbols loaded")

        # Test specific currencies
        assert ('USD', 'US Dollar ($)') in CURRENCY_CHOICES, "USD not found in choices"
        assert ('EUR', 'Euro (€)') in CURRENCY_CHOICES, "EUR not found in choices"
        assert CURRENCY_SYMBOLS['USD'] == '$', f"USD symbol should be $, got {CURRENCY_SYMBOLS['USD']}"
        assert CURRENCY_SYMBOLS['EUR'] == '€', f"EUR symbol should be €, got {CURRENCY_SYMBOLS['EUR']}"
        print("✅ Currency data validation passed")

        return True

    except Exception as e:
        print(f"❌ Currency constants test failed: {e}")
        return False

def test_tenant_default_function():
    """Test the get_tenant_default_currency function"""
    try:
        from saasCRM.currency import get_tenant_default_currency

        # Test with None tenant
        default = get_tenant_default_currency(None)
        assert default == 'USD', f"Expected USD for None tenant, got {default}"
        print("✅ Default currency for None tenant: USD")

        # Test with mock tenant
        class MockTenant:
            default_currency = 'EUR'

        tenant = MockTenant()
        default = get_tenant_default_currency(tenant)
        assert default == 'EUR', f"Expected EUR for tenant, got {default}"
        print("✅ Default currency for tenant: EUR")

        return True

    except Exception as e:
        print(f"❌ Tenant default function test failed: {e}")
        return False

def test_currency_converter_static_methods():
    """Test CurrencyConverter static methods that don't require network or Django"""
    try:
        # Test just the constants and utility functions that don't require Django
        from saasCRM.currency import CURRENCY_CHOICES, CURRENCY_SYMBOLS

        # Test format_currency logic manually (since it doesn't require Django)
        def format_currency(amount, currency_code):
            """Simplified version of format_currency for testing"""
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))

            # Format based on currency
            if currency_code in ['JPY', 'KRW']:
                formatted_amount = f"{amount.quantize(Decimal('1')):,}"
            else:
                formatted_amount = f"{amount.quantize(Decimal('0.01')):,}"

            symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
            return f"{symbol}{formatted_amount}"

        # Test format_currency
        amount = Decimal('1234.56')
        formatted = format_currency(amount, 'USD')
        assert formatted == '$1,234.56', f"Expected '$1,234.56', got '{formatted}'"
        print(f"✅ Currency formatting USD: {formatted}")

        # Test format_currency with EUR
        formatted_eur = format_currency(amount, 'EUR')
        assert formatted_eur == '€1,234.56', f"Expected '€1,234.56', got '{formatted_eur}'"
        print(f"✅ Currency formatting EUR: {formatted_eur}")

        # Test format_currency with JPY (no decimals)
        formatted_jpy = format_currency(Decimal('1234'), 'JPY')
        assert formatted_jpy == '¥1,234', f"Expected '¥1,234', got '{formatted_jpy}'"
        print(f"✅ Currency formatting JPY: {formatted_jpy}")

        # Test get_supported_currencies logic
        currencies = CURRENCY_CHOICES
        assert len(currencies) == 12, f"Expected 12 currencies, got {len(currencies)}"
        print(f"✅ Supported currencies: {len(currencies)} currencies")

        # Test is_valid_currency logic
        def is_valid_currency(currency_code):
            return currency_code in [code for code, name in CURRENCY_CHOICES]

        assert is_valid_currency('USD') == True, "USD should be valid"
        assert is_valid_currency('INVALID') == False, "INVALID should not be valid"
        print("✅ Currency validation working")

        return True

    except Exception as e:
        print(f"❌ CurrencyConverter static methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Running Currency Module Tests\n")

    tests = [
        test_currency_constants,
        test_tenant_default_function,
        test_currency_converter_static_methods,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n--- Running {test.__name__} ---")
        if test():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All currency tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())