"""
Currency utilities for multi-currency support in DjangoCRM.
Provides exchange rate handling and currency conversion functionality.
"""

from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)

# Supported currencies with their symbols
CURRENCY_CHOICES = [
    ('USD', 'US Dollar ($)'),
    ('EUR', 'Euro (€)'),
    ('GBP', 'British Pound (£)'),
    ('JPY', 'Japanese Yen (¥)'),
    ('CAD', 'Canadian Dollar (C$)'),
    ('AUD', 'Australian Dollar (A$)'),
    ('CHF', 'Swiss Franc (CHF)'),
    ('CNY', 'Chinese Yuan (¥)'),
    ('INR', 'Indian Rupee (₹)'),
    ('BRL', 'Brazilian Real (R$)'),
    ('ZAR', 'South African Rand (R)'),
    ('KES', 'Kenyan Shilling (KSh)'),
]

# Currency symbols mapping
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'C$',
    'AUD': 'A$',
    'CHF': 'CHF',
    'CNY': '¥',
    'INR': '₹',
    'BRL': 'R$',
    'ZAR': 'R',
    'KES': 'KSh',
}

class CurrencyConverter:
    """
    Handles currency conversion with exchange rates.
    Uses fixer.io API for real-time rates, with caching.
    """

    CACHE_KEY = 'currency_rates'
    CACHE_TIMEOUT = 3600  # 1 hour

    @classmethod
    def get_exchange_rates(cls, base_currency='USD'):
        """
        Get exchange rates from cache or API.
        Returns rates relative to base_currency.
        """
        try:
            from django.core.cache import cache
            cache_key = f"{cls.CACHE_KEY}_{base_currency}"
            rates = cache.get(cache_key)

            if rates is None:
                rates = cls._fetch_exchange_rates(base_currency)
                if rates:
                    cache.set(cache_key, rates, cls.CACHE_TIMEOUT)

            return rates or {}
        except ImportError:
            # Fallback when Django is not available
            return cls._get_fallback_rates(base_currency)

    @classmethod
    def _fetch_exchange_rates(cls, base_currency='USD'):
        """
        Fetch exchange rates from external API.
        """
        try:
            import requests
            # Using exchangerate-api.com (free tier)
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('rates', {})
            else:
                logger.warning(f"Failed to fetch exchange rates: {response.status_code}")
                return cls._get_fallback_rates(base_currency)

        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            return cls._get_fallback_rates(base_currency)

    @classmethod
    def _get_fallback_rates(cls, base_currency='USD'):
        """
        Provide fallback exchange rates when API is unavailable.
        These are approximate rates and should be updated periodically.
        """
        # Fallback rates relative to USD (as of 2024)
        fallback_rates = {
            'USD': Decimal('1.0'),
            'EUR': Decimal('0.85'),
            'GBP': Decimal('0.73'),
            'JPY': Decimal('110.0'),
            'CAD': Decimal('1.25'),
            'AUD': Decimal('1.35'),
            'CHF': Decimal('0.92'),
            'CNY': Decimal('6.45'),
            'INR': Decimal('74.5'),
            'BRL': Decimal('5.2'),
            'ZAR': Decimal('14.8'),
            'KES': Decimal('129.0'),
        }

        if base_currency == 'USD':
            return fallback_rates
        else:
            # Convert to base_currency rates
            base_rate = fallback_rates.get(base_currency, Decimal('1.0'))
            return {currency: rate / base_rate for currency, rate in fallback_rates.items()}

    @classmethod
    def convert_amount(cls, amount, from_currency, to_currency, tenant=None):
        """
        Convert amount from one currency to another.

        Args:
            amount (Decimal): Amount to convert
            from_currency (str): Source currency code
            to_currency (str): Target currency code
            tenant: Tenant object (for future tenant-specific rates)

        Returns:
            Decimal: Converted amount
        """
        if from_currency == to_currency:
            return amount

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        rates = cls.get_exchange_rates('USD')

        # Convert to USD first, then to target currency
        usd_amount = amount
        if from_currency != 'USD':
            from_rate = rates.get(from_currency)
            if from_rate:
                usd_amount = amount / Decimal(str(from_rate))

        if to_currency == 'USD':
            return usd_amount

        to_rate = rates.get(to_currency)
        if to_rate:
            return (usd_amount * Decimal(str(to_rate))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # If conversion fails, return original amount
        logger.warning(f"Currency conversion failed: {from_currency} to {to_currency}")
        return amount

    @classmethod
    def format_currency(cls, amount, currency_code, include_symbol=True):
        """
        Format amount with currency symbol and proper formatting.

        Args:
            amount (Decimal): Amount to format
            currency_code (str): Currency code
            include_symbol (bool): Whether to include currency symbol

        Returns:
            str: Formatted currency string
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Format based on currency
        if currency_code in ['JPY', 'KRW']:
            # No decimal places for these currencies
            formatted_amount = f"{amount.quantize(Decimal('1')):,}"
        else:
            formatted_amount = f"{amount.quantize(Decimal('0.01')):,}"

        if include_symbol:
            symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
            return f"{symbol}{formatted_amount}"

        return formatted_amount

    @classmethod
    def get_supported_currencies(cls):
        """
        Get list of supported currencies.
        """
        return CURRENCY_CHOICES

    @classmethod
    def is_valid_currency(cls, currency_code):
        """
        Check if currency code is supported.
        """
        return currency_code in [code for code, name in CURRENCY_CHOICES]


def get_tenant_default_currency(tenant):
    """
    Get the default currency for a tenant.
    """
    if tenant and hasattr(tenant, 'default_currency'):
        return tenant.default_currency
    return 'USD'