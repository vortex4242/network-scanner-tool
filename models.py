from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import json
from typing import List, Dict, Any

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the given Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    scans = db.relationship('ScanResult', backref='user', lazy=True)

class ScanResult(db.Model):
    """Model to store network scan results."""
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    _ports = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def ports(self) -> List[Dict[str, Any]]:
        """Get the ports as a list of dictionaries."""
        return json.loads(self._ports) if self._ports else []

    @ports.setter
    def ports(self, value: List[Dict[str, Any]]):
        """Set the ports from a list of dictionaries."""
        self._ports = json.dumps(value)

    def __repr__(self):
        return f'<ScanResult {self.id} {self.host}>'
