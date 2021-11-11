from database import db
from sqlalchemy.sql import func

class Camera_Algorithm(db.Model):
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(300), nullable=False)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithm.id"), nullable=False)

class Algorithm(db.Model):
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String(200), unique=True, nullable=False)
    weights_path = db.Column(db.String(2038), nullable=False)

    def __repr__(self):
        return '<Algorithm %r>' % self.algorithm

class Record(db.Model):
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(300), nullable=False)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithm.id"), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    record_path = db.Column(db.String(2038), nullable=False)
