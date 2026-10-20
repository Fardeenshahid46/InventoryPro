from app.extensions import db
from app.models.setting import Setting, SettingType


class SettingService:
    """Manages application-wide persistent configuration."""

    DEFAULT_SETTINGS = [
        ("company_name", "InventoryPro Enterprise", SettingType.STRING, "Company or store display name"),
        ("default_currency", "PKR", SettingType.STRING, "Default system currency prefix"),
        ("low_stock_threshold", "10", SettingType.INTEGER, "Default threshold for low stock alerts"),
        ("items_per_page", "25", SettingType.INTEGER, "Pagination count for tables"),
    ]

    @staticmethod
    def init_defaults():
        """Ensure all standard application settings exist in database."""
        for key, value, data_type, description in SettingService.DEFAULT_SETTINGS:
            existing = Setting.query.filter_by(key=key).first()
            if not existing:
                setting = Setting(
                    key=key,
                    value=value,
                    data_type=data_type,
                    description=description,
                )
                db.session.add(setting)
        db.session.commit()

    @staticmethod
    def get(key: str, default=None):
        """Retrieve a setting value cast to its appropriate Python type."""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            return setting.get_typed_value()
        return default

    @staticmethod
    def set(key: str, value: str, description=None, data_type=SettingType.STRING):
        """Update or insert a setting record."""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = Setting(
                key=key,
                value=str(value),
                data_type=data_type,
                description=description,
            )
            db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def get_all():
        """Get all settings as a dictionary keyed by key."""
        settings = Setting.query.all()
        return {s.key: s for s in settings}
