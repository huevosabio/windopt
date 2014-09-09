import datetime
from flask import url_for
from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class User(db.Document):
    """User Schema"""
    email = db.StringField(primary_key=True)
    password_hash = db.StringField(required=True)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None #valid token, but expired
        except BadSignature:
            return None #invalic token
        user = db.User.objects.with_id(data['id'])
        return user

class Shapelayer(db.Document):
    """Shapefile storing files and information"""
    layername = db.StringField(required = True)
    shx = db.FileField()
    shp = db.FileField()
    dbf = db.FileField()
    prj = db.FileField()
    logic = db.StringField(required=True)
    cost = db.FloatField()

class Project(db.Document):
    """Project Schema"""
    name = db.StringField(unique=True)
    auth = db.ReferenceField(User)
    layers = db.ListField(db.ReferenceField(Shapelayer))
    winddata = db.FileField()