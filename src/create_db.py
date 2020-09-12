from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.festival_is import app

db = SQLAlchemy(app)


class Festival(db.Model):
    __tablename__ = "festival"
    fest_id = db.Column("fest_id", db.Integer, primary_key=True)
    description = db.Column("description", db.Text)
    style = db.Column("style", db.String(10))
    address = db.Column("address", db.Text, nullable=False)
    cost = db.Column("cost", db.Integer, nullable=False, default=0)
    time_from = db.Column("time_from", db.Date, nullable=False)
    time_to = db.Column("time_to", db.Date, nullable=False)
    capacity = db.Column("capacity", db.Integer, nullable=False, default=1000)
    age_restriction = db.Column("age_restriction", db.Integer, nullable=False)


class Stage(db.Model):
    __tablename__ = "stage"
    stage_id = db.Column("stage_id", db.Integer, primary_key=True)
    size = db.Column("size", db.Integer)


class Band(db.Model):
    __tablename__ = "band"
    band_id = db.Column("band_id", db.Integer, primary_key=True)
    name = db.Column("name", db.Text(20), nullable=False)
    logo = db.Column("logo", db.Text, nullable=False)
    scores = db.Column("scores", db.Integer, nullable=False, default=1)
    genre = db.Column("genre", db.Text, nullable=False)
    tags = db.Column("tags", db.Text(10))

    def __repr__(self):
        return f"<Band {self.band_id}: {self.name}>"


class Performance(db.Model):
    __tablename__ = "performance"
    perf_id = db.Column("perf_id", db.Integer, primary_key=True)
    fk_fest_id = db.Column(
        "fk_fest_id", db.Integer, db.ForeignKey("festival.fest_id"), nullable=False
    )
    fk_band_id = db.Column(
        "fk_band_id", db.Integer, db.ForeignKey("band.band_id"), nullable=False
    )
    fk_stage_id = db.Column(
        "fk_stage_id", db.Integer, db.ForeignKey("stage.stag_id"), nullable=False
    )

    fest = db.relationship("Festival", foreign_keys=fk_fest_id)  # backref ?
    band = db.relationship("Band", foreign_keys=fk_band_id)  # backref ?
    stage = db.relationship("Stage", foreign_keys=fk_stage_id)  # backref ?


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    name = db.Column("name", db.Text(10), nullable=False)
    surname = db.Column("surname", db.Text(25), nullable=False)
    permissions = db.Column("permissions", db.Integer, nullable=False)


class Ticket(db.Model):
    __tablename__ = "ticket"
    ticket_id = db.Column("ticket_id", db.Integer, primary_key=True)
    fk_user_id = db.Column(
        "fk_user_id", db.Integer, db.ForeignKey("user.user_id"), nullable=False
    )
    fk_t_fest_id = db.Column(
        "fk_t_stage_id", db.Integer, db.ForeignKey("festival.fest_id"), nullable=False
    )

    user = db.relationship("User", foreign_keys=fk_user_id)
    t_fest = db.relationship("Festival", foreign_keys=fk_t_fest_id)

