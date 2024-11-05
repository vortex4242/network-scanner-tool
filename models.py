from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(100))
    host = db.Column(db.String(100))
    state = db.Column(db.String(20))
    _ports = db.Column(db.Text)

    @property
    def ports(self):
        return json.loads(self._ports) if self._ports else []

    @ports.setter
    def ports(self, value):
        self._ports = json.dumps(value)
