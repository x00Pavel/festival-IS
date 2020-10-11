from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    ForeignKey,
    String,
    Boolean,
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
    max_capacity = db.Column("max_capacity", db.Integer, nullable=False, default=1000)
    current_ticket_count = db.Column(
        "current_ticket_count", db.Integer, nullable=False, default=0
    )
    age_restriction = db.Column("age_restriction", db.Integer, nullable=False)

    def __init__(
        self,
        fest_name,
        description,
        style,
        address,
        cost,
        time_from,
        time_to,
        max_capacity=1000,
        current_ticket_count=0,
    ):
        self.fest_name = fest_name
        self.description = description
        self.style = style
        self.address = address
        self.cost = cost
        self.time_from = time_from
        self.time_to = time_to
        self.max_capacity = max_capacity
        self.current_ticket_count = current_ticket_count

    def __repr__(self):
        return f"{self.fest_id}, {self.description}, {self.style}, {self.address}, {self.cost}, {self.time_from}, {self.time_to}, {self.max_capacity}, {self.age_restriction}"

    @classmethod
    def get_festival(self, fest_id):
        return Festival.query.filter_by(fest_id=fest_id).first()


class Stage(db.Model):
    __tablename__ = "Stage"
    stage_id = db.Column("stage_id", db.Integer, primary_key=True)
    size = db.Column("size", db.Integer)

    def __init__(self, size):
        self.size = size

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

    def __init__(self, name, logo, scores, genre, tags):
        self.name = name
        self.logo = logo
        self.scores = scores
        self.genre = genre
        self.tags = tags

    def __repr__(self):
        return f"Band {self.band_id}: {self.name}"

    # @classmethod
    # def get_band(band_id):
    #     pass


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

    def __init__(self, fest_id, stage_id, band_id):
        # TODO check if given numbers exist in corresponding tables
        self.fest_id = fest_id
        self.stage_id = stage_id
        self.band_id = band_id

    def __repr__(self):
        return f"Performance {self.perf_id}: festival_id: {self.fk_fest_id}; stage_id: {self.fk_stage_id}; band_id: {self.fk_band_id}"


class User(UserMixin, db.Model):
    __tablename__ = "User"

    user_id = Column("user_id", Integer, primary_key=True)
    user_email = db.Column("user_email", db.Text, nullable=False, unique=True)
    name = db.Column("name", db.Text, nullable=False)
    surname = db.Column("surname", db.Text, nullable=False)
    passwd = db.Column("passwd", db.Text, nullable=False)
    avatar = db.Column(
        "avatar",
        db.Text,
        nullable=False,
        default="https://festival-static.s3-eu-west-1.amazonaws.com/default_avatar.png",
    )
    perms = Column("perms", Integer, nullable=False)
    address = Column("address", String(50), nullable=False)

    __mapper_args__ = {"polymorphic_identity": 4, "polymorphic_on": perms}
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

    @classmethod
    def register(cls, form, perms):
        email = form.email.data
        name = form.firstname.data
        surname = form.lastname.data
        passwd_hash = generate_password_hash(form.password.data, method="sha256")
        address = f"{form.city.data}, {form.street.data} ({form.streeta.data if form.streeta is not None else 'No additional street' }), {form.homenum.data}"
        table = None
        if perms == 4:
            table = User
        elif perms == 2:
            table = Organizer
        new_user = table(
            user_email=email,
            name=name,
            surname=surname,
            perms=perms,
            passwd=passwd_hash,
            address=address,
            avatar=None,
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user


    def reserve_ticket(self, fest_id):
        # TODO Send request for reservation to seller
        ticket = Ticket(self.user_id, fest_id)
        db.session.add(ticket)
        fest = Festival.query.filter_by(fest_id=fest_id).first()
        if fest.current_ticket_count != fest.max_capacity:
            fest.current_ticket_count += 1
        else:
            raise ValueError("Festival is already out of tickets")
        db.session.commit()

    def get_tickets(self):
        today = date.today()
        actual_tickets = []
        outdated_tickets = []
        tickets = Ticket.query.filter_by(user_id=self.user_id).all()
        for ticket in tickets:
            if (ticket.fest.time_from >= today):
                actual_tickets.append(ticket)
            else:
                outdated_tickets.append(ticket)
        return actual_tickets, outdated_tickets

        
class Seller(User):
    __tablename__ = "Seller"
    __mapper_args__ = {
        "polymorphic_identity": 3,
    }

    seller_id = Column(
        "seller_id", Integer, ForeignKey("User.user_id"), primary_key=True
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.seller_id = self.get_id()

    def get_tickets(self, fest_id=None, user_id=None):
        if fest_id is not None and user_id is not None:
            return Ticket.query.filter(fest_id == fest_id, user_id == user_id)
        elif fest_id is not None:
            return Ticket.query.filter_by(fest_id=fest_id)
        elif user_id is not None:
            return Ticket.query.filter_by(user_id=user_id)
        else:
            return Ticket.query.all()

    def approve_ticket(self):
        pass


class Organizer(Seller):
    __tablename__ = "Organizer"
    __mapper_args__ = {
        "polymorphic_identity": 2,
    }

    # ForeignKeyConstraint(["org_id"], ["Seller.seller_id"])
    org_id = Column("org_id", Integer, ForeignKey("Seller.seller_id"), primary_key=True)

    def __init__(self, **kwargs):
        super(Seller, self).__init__(**kwargs)
        self.org_id = self.get_id()

    def get_sellers(self):
        return [row for row in Seller.query.all()]

    def add_seller(self, **kwargs):
        email = form.email.data
        name = form.firstname.data
        surname = form.lastname.data
        passwd_hash = generate_password_hash(form.password.data, method="sha256")
        address = f"{form.city.data}, {form.street.data} ({form.streeta.data if form.streeta is not None else 'No additional street' }), {form.homenum.data}"

        seller = Seller(user_email=email,
            name=name,
            surname=surname,
            perms=3,
            passwd=passwd_hash,
            address=address,
            avatar=None,)
        db.session.add(seller)
        db.session.commit()

    def add_fest(self):
        pass

    def add_stage(self):
        pass

    def add_band(self):
        pass


class Admin(Organizer):
    __tablename__ = "Admin"
    __mapper_args__ = {
        "polymorphic_identity": 1,
    }

    admin_id = Column(
        "admin_id", Integer, ForeignKey("Organizer.org_id"), primary_key=True
    )

    def __init__(self, **kwargs):
        super(Organizer, self).__init__(**kwargs)
        self.admin_id = self.get_id()

    def add_organizer(self):
        pass

    def delete_user(self):
        pass

    def list_users(self):
        pass


class RootAdmin(Admin):
    """Reperesentation of root admin. Only this role can add new admins"""

    __tablename__ = "RootAdmin"
    __mapper_args__ = {
        "polymorphic_identity": 0,
    }

    root_admin_id = Column(
        "root_admin_id", Integer, ForeignKey("Admin.admin_id"), primary_key=True
    )

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        root_admin_id = self.get_id()

    def add_admin(self):
        pass


class Ticket(db.Model):
    """Representation of ticket on festival

    Attributes:
        ticket_id (int): unique ID of ticket
        fk_user_email (string): email of user, that bought this ticket
        fk_fest_id (int): festival ID ticket corresponds to
    """

    __tablename__ = "Ticket"
    ticket_id = db.Column("ticket_id", db.Integer, primary_key=True)
    approved = Column("approved", Boolean, nullable=False, default=False)
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


class SellersList(db.Model):
    __tablename__ = "SellerList"
    entry_id = Column("entry_id", Integer, primary_key=True)
    fest_id = Column("fest_id", Integer, ForeignKey("Festival.fest_id"), nullable=False)
    seller_id = Column(
        "seller_id", Integer, ForeignKey("Seller.seller_id"), nullable=False
    )

    fest = relationship("Festival", foreign_keys=fest_id)
    seller = relationship("Seller", foreign_keys=seller_id)

    def __init__(self, fest_id: int, seller_id: int):
        self.fest_id = fest_id
        self.seller_id = seller_id

    def __repr__(self):
        return f"Entry ID: {self.entry_id} - Seller id: {self.seller_id} -> Festival ID: {self.fest_id}"


class BandMember(db.Model):
    """Representaton of music band member
    One member can be a member only for one band
    """

    __tablename__ = "BandMember"
    person_id = Column("person_id", Integer, primary_key=True)
    band_id = Column("band_id", Integer, ForeignKey("Band.band_id"), nullable=False)
    name = Column("name", String(10), nullable=False)
    surname = Column("surname", String(10), nullable=False)

    band = relationship("Band", foreign_keys=band_id)

    def __init__(self, person_id: int, band_id: int, name: str, surname: str):
        self.band_id = band_id
        self.name = name
        self.surname = surname

    def __repr__(self):
        return (
            f"Band member {self.person_id}: {self.name}, {self.surname}, {self.band_id}"
        )
