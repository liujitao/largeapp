# -*- coding: utf-8 -*-

from app import db, app

from Crypto.Cipher import AES
import base64

secret_key = app.config['SECRET_KEY']
cipher = AES.new(secret_key, AES.MODE_ECB)

class Base(db.Model):
    __abstract__ = True
    uuid = db.Column(db.String(32), primary_key=True)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

class Host(Base):
    __tablename__ = 'host'
    name = db.Column(db.String(40), index=True)
    ip = db.Column(db.String(15))
    port = db.Column(db.String(5))
    password_hash = db.Column(db.String(128))
    status = db.Column(db.Integer, default=0)
    last_check_time = db.Column(db.DateTime)

    @property
    def password(self):
        return cipher.decrypt(base64.b64decode(self.password_hash)).strip().decode()

    @password.setter
    def password(self, password):
        self.password_hash = base64.b64encode(cipher.encrypt(password.rjust(32)))