
from database import db

class Algorithm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String(200), unique=True, nullable=False)
    weights_path = db.Column(db.String(2038), nullable=False)

    def __repr__(self):
        return '<Algorithm %r>' % self.algorithm

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(300), unique=True, nullable=False)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithm.id"), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False)
    record_path = db.Column(db.String(2038), nullable=False)
