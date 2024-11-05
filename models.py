rom flask_login import UserMixin
from . import db
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(100))
    state = db.Column(db.String(20))
    _ports = db.Column(db.Text)

    @property
    def ports(self):
        return json.loads(self._ports)

    @ports.setter
    def ports(self, value):
        self._ports = json.dumps(value)
