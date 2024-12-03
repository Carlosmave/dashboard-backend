import os, csv
from flask import Flask
from flask_cors import CORS
from .routes import rest_api
from .models import db, IrisData

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('api.config.BaseConfig')
    db.init_app(app)
    rest_api.init_app(app)
    CORS(app)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    with app.app_context():
        db.create_all()
        # initial data load
        if not IrisData.query.all():
            with open('iris.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    iris_data_item = IrisData(
                        sepal_length = row['sepal.length'],
                        sepal_width = row['sepal.width'],
                        petal_length = row['petal.length'],
                        petal_width = row['petal.width'],
                        variety = row['variety']
                    )
                    iris_data_item.save()
    return app