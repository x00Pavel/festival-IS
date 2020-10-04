from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    ForeignKey,
    String,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship
from festival_is import app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)


class Festival(db.Model):
    __tablename__ = "Festival"

    fest_id = db.Column("fest_id", db.Integer, primary_key=True)
    fest_name = Column("fest_name", Text, nullable=False)
    description = db.Column("description", db.Text)
    style = db.Column("style", db.String(10))
    address = db.Column("address", db.Text, nullable=False)
    cost = db.Column("cost", db.Integer, nullable=False, default=0)
    time_from = db.Column("time_from", db.Date, nullable=False)
    time_to = db.Column("time_to", db.Date, nullable=False)
    capacity = db.Column("capacity", db.Integer, nullable=False, default=1000)
    age_restriction = db.Column("age_restriction", db.Integer, nullable=False)

    # TODO: tmp representation.
    def __repr__(self):
        return f"{self.fest_id}, {self.description}, {self.style}, {self.address}, {self.cost}, {self.time_from}, {self.time_to}, {self.capacity}, {self.age_restriction}"


class Stage(db.Model):
    __tablename__ = "Stage"
    stage_id = db.Column("stage_id", db.Integer, primary_key=True)
    size = db.Column("size", db.Integer)

    def __repr__(self):
        return f"Stager {self.stage_id}: size: {self.size}"


class Band(db.Model):
    __tablename__ = "Band"
    band_id = db.Column("band_id", db.Integer, primary_key=True)
    name = db.Column("name", db.Text, nullable=False)
    logo = db.Column("logo", db.Text, nullable=False)
    scores = db.Column("scores", db.Integer, nullable=False, default=1)
    genre = db.Column("genre", db.Text, nullable=False)
    tags = db.Column("tags", db.Text)

    def __repr__(self):
        return f"<Band {self.band_id}: {self.name}>"


class Performance(db.Model):
    __tablename__ = "Performance"
    perf_id = db.Column("perf_id", db.Integer, primary_key=True)
    fest_id = db.Column(
        "fest_id", db.Integer, db.ForeignKey("Festival.fest_id"), nullable=False
    )
    stage_id = db.Column(
        "stage_id", db.Integer, db.ForeignKey("Stage.stage_id"), nullable=False
    )
    band_id = db.Column(
        "band_id", db.Integer, db.ForeignKey("Band.band_id"), nullable=False
    )
    # time_from = db.Column("time_from", db.Date, nullable=False) TODO also edit CSV for performances
    # time_to = db.Column("time_to", db.Date, nullable=False)

    fest = db.relationship("Festival", foreign_keys=fest_id)  # backref ?
    band = db.relationship("Band", foreign_keys=band_id)  # backref ?
    stage = db.relationship("Stage", foreign_keys=stage_id)  # backref ?

    def __repr__(self):
        return f"Performance {self.perf_id}: festival_id: {self.fk_fest_id}; stage_id: {self.fk_stage_id}; band_id: {self.fk_band_id}"


class User(UserMixin, db.Model):
    __tablename__ = "User"

    user_id = Column("user_id", Integer, primary_key=True)
    user_email = db.Column("user_email", db.Text, nullable=False)
    name = db.Column("name", db.Text, nullable=False)
    surname = db.Column("surname", db.Text, nullable=False)
    passwd = db.Column("passwd", db.Text, nullable=False)
    avatar = db.Column(
        "avatar",
        db.Text,
        nullable=False,
        default="https://festival-static.s3-eu-west-1.amazonaws.com/default_avatar.png",
    )
    perms = Column("perms", String(20), nullable=False)
    address = Column("address", String(50), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "User", "polymorphic_on": perms}
    _is_authenticated = True
    _is_active = True
    _is_anonymous = False

    def __init__(self, user_email, name, surname, perms, passwd, address, avatar=None):
        self.user_email = user_email
        self.name = name
        self.surname = surname
        self.perms = perms
        self.passwd = passwd
        self.avatar = avatar
        self.address = address

    def __repr__(self):
        return f"{self.perms} {self.user_id}: {self.name} {self.surname}"

    def get_id(self):
        return self.user_id

    @classmethod
    def find_by_email(cls, email):
        return User.query.filter_by(user_email=email).first()

    def set_password(self, password):
        self.passwd = generate_password_hash(password, method="sha256")

    def check_passwd(self, password):
        """Check hashed password."""
        return check_password_hash(self.passwd, password)

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, val):
        self._is_authenticated = val

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, val):
        self._is_active = val

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @is_anonymous.setter
    def is_anonymous(self, val):
        self._is_anonymous = val

    def reserve_ticket(self, fest_id):
        ticket = Ticket(self.user_id, fest_id)
        db.session.add(ticket)
        db.session.commit()


class Seller(User):
    __tablename__ = "Seller"
    __mapper_args__ = {
        "polymorphic_identity": "Seller",
    }

    seller_id = Column(
        "seller_id", Integer, ForeignKey("User.user_id"), primary_key=True
    )
    # ForeignKeyConstraint(
    #     ["seller_id"], ["invoice.invoice_id", "invoice.ref_num"]
    # )
    # fest_id = Column("fest_id", Integer, ForeignKey("Festival.fest_id"), nullable=False)
    # fest = relationship("Festival", foreign_keys=fest_id)

    def __init__(self, *args):
        super(User, self).__init__(*args)
        self.seller_id = self.get_id()


class Organizer(Seller):
    __tablename__ = "Organizer"
    __mapper_args__ = {
        "polymorphic_identity": "Organizer",
    }

    # ForeignKeyConstraint(["org_id"], ["Seller.seller_id"])
    org_id = Column("org_id", Integer, ForeignKey("Seller.seller_id"), primary_key=True)

    def __init__(self, *args):
        super(Seller, self).__init__(*args)
        self.org_id = self.get_id()


class Admin(Organizer):
    __tablename__ = "Admin"
    __mapper_args__ = {
        "polymorphic_identity": "Admin",
    }

    admin_id = Column(
        "admin_id", Integer, ForeignKey("Organizer.org_id"), primary_key=True
    )

    def __init__(self, *args):
        super(Organizer, self).__init__(*args)
        self.admin_id = self.get_id()


class RootAdmin(Admin):
    """Reperesentation of root admin. Only this role can add new admins
    WARNING: Not need __inti__ method, because this user is hardcoded
    """

    __tablename__ = "RootAdmin"
    __mapper_args__ = {
        "polymorphic_identity": "RootAdmin",
    }

    root_admin_id = Column(
        "root_admin_id", Integer, ForeignKey("Admin.admin_id"), primary_key=True
    )

    def __init__(self, *args):
        super(Admin, self).__init__(*args)
        root_admin_id = self.get_id()


class Ticket(db.Model):
    """Representation of ticket on festival

    Attributes:
        ticket_id (int): unique ID of ticket
        fk_user_email (string): email of user, that bought this ticket
        fk_fest_id (int): festival ID ticket corresponds to
    """

    __tablename__ = "Ticket"
    ticket_id = db.Column("ticket_id", db.Integer, primary_key=True)
    user_id = db.Column(
        "user_id", Integer, db.ForeignKey("User.user_id"), nullable=False
    )
    fest_id = db.Column(
        "fest_id", Integer, db.ForeignKey("Festival.fest_id"), nullable=False
    )

    user = db.relationship("User", foreign_keys=user_id)
    fest = db.relationship("Festival", foreign_keys=fest_id)

    def __init__(self, user_id, fest_id):
        self.user_id = user_id
        self.fest_id = fest_id

    def __repr__(self):
        return f"Ticket {self.ticket_id}: user_id: {self.user_id}; festival_id: {self.fest_id}"


# TODO
class SellersList:
    pass


# TODO
class BandMember:
    """Representaton of music band member
    One member can be a member only for one band
    """

    __tablename__ = "BandMember"

    def __init__(self, person_id: int, band_id: int, name: str, surname: str):
        """[summary]

        Args:
            person_id (int):
            band_id (int):
            name (str):
            surname (str):
        """
        self.person_id = person_id
        self.band_id = band_id
        self.name = name
        self.surname = surname
