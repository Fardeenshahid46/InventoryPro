from datetime import datetime
import secrets


def format_currency(value, currency="PKR"):
    """Format decimal or float value as a currency string (e.g. 'PKR 1,250.00')."""
    if value is None:
        return f"{currency} 0.00"
    try:
        val = float(value)
        return f"{currency} {val:,.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"


def format_datetime(value, format_str="%Y-%m-%d %H:%M"):
    """Format a datetime object into a user-friendly string."""
    if not value or not isinstance(value, datetime):
        return ""
    return value.strftime(format_str)


def generate_transaction_code(prefix="TXN"):
    """
    Generate a unique, collision-resistant transaction code.
    Format: TXN-YYYYMMDD-XXXX (e.g. TXN-20261021-A39F)
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    random_hex = secrets.token_hex(2).upper()
    return f"{prefix}-{date_str}-{random_hex}"
