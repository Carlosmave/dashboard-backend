from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.Text())
    variety = db.Column(db.String(32), nullable=False)
    jwt_auth_active = db.Column(db.Boolean())

    def __repr__(self):
        return f"{self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def to_dict(self):
        cls_dict = {}
        cls_dict['id'] = self.id
        cls_dict['email'] = self.email
        cls_dict['variety'] = self.variety
        return cls_dict

    def to_json(self):
        return self.to_dict()


class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class IrisData(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    sepal_length = db.Column(db.Float(), nullable=False)
    sepal_width = db.Column(db.Float(), nullable=False)
    petal_length = db.Column(db.Float(), nullable=False)
    petal_width = db.Column(db.Float(), nullable=False)
    variety = db.Column(db.String(32), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def filter_by_variety(cls, variety):
        return cls.query.filter_by(variety=variety)

    def to_dict(self):
        cls_dict = {}
        cls_dict['sepal_length'] = self.sepal_length
        cls_dict['sepal_width'] = self.sepal_width
        cls_dict['petal_length'] = self.petal_length
        cls_dict['petal_width'] = self.petal_width
        return cls_dict

    def to_json(self):
        return self.to_dict()