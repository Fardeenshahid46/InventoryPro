from datetime import datetime
from app.extensions import db


class SettingType:
    STRING = "STRING"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"


class Setting(db.Model):
    """Dynamic key-value configuration setting."""
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    data_type = db.Column(db.String(20), default=SettingType.STRING, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def get_typed_value(self):
        """Convert stored string into appropriate Python data type."""
        if self.data_type == SettingType.INTEGER:
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.data_type == SettingType.BOOLEAN:
            return self.value.lower() in ("true", "1", "yes")
        return self.value

    def __repr__(self):
        return f"<Setting key='{self.key}' value='{self.value}'>"
