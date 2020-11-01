from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    DateTime,
    ForeignKey,
    String,
    Boolean,
    ForeignKeyConstraint,
    or_,
    and_,
)
from sqlalchemy.orm import relationship, backref
from festival_is import app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)


class Festival(db.Model):
    __tablename__ = "Festival"

    fest_id = db.Column("fest_id", db.Integer, primary_key=True)
    fest_name = Column("fest_name", Text, nullable=False)
    fest_logo = Column("fest_logo", Text, nullable=False)
    description = db.Column("description", db.Text)
    style = db.Column("style", db.String(10))
    address = db.Column("address", db.Text, nullable=False)
    cost = db.Column("cost", db.Integer, nullable=False, default=0)
    time_from = db.Column("time_from", db.DateTime, nullable=False)
    time_to = db.Column("time_to", db.DateTime, nullable=False)
    max_capacity = db.Column("max_capacity", db.Integer, nullable=False, default=1000)
    current_ticket_count = db.Column(
        "current_ticket_count", db.Integer, nullable=False, default=0
    )
    age_restriction = db.Column("age_restriction", db.Integer, nullable=False)
    sale = db.Column("sale", db.Integer, nullable=False, default=0)
    org_id = Column("org_id", Integer, ForeignKey("Organizer.org_id"), nullable=False)
    status = Column("status", Integer, default=0)

    organizer = relationship("Organizer", foreign_keys=org_id)

    def __repr__(self):
        return f"{self.fest_id}, {self.description}, {self.style}, {self.address}, {self.cost}, {self.time_from}, {self.time_to}, {self.max_capacity}, {self.age_restriction}, {self.sale}"

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
    logo = db.Column("logo", db.Text, nullable=False, default="No logo")
    scores = db.Column("scores", db.Integer, nullable=False, default=1)
    genre = db.Column("genre", db.Text, nullable=False)
    tags = db.Column("tags", db.Text)
    deleted_on = Column("deleted_on", Date, default=None)
    created_on = Column(
        "created_on", Date, nullable=False, default=datetime.now().strftime("%x")
    )

    def __repr__(self):
        return f"Band {self.band_id}: {self.name}"


class Performance(db.Model):
    __tablename__ = "Performance"
    perf_id = db.Column("perf_id", db.Integer, primary_key=True)
    fest_id = db.Column(
        "fest_id", db.Integer, db.ForeignKey("Festival.fest_id"), nullable=False
    )
    stage_id = db.Column(
        "stage_id", db.Integer, db.ForeignKey("Stage.stage_id"), nullable=False
    )
    band_id = db.Column("band_id", db.Integer, db.ForeignKey("Band.band_id"))
    canceled = Column("canceled", Boolean, default=False)
    time_from = Column(
        "time_from", DateTime, nullable=False
    )  # TODO also edit CSV for performances
    time_to = Column("time_to", DateTime, nullable=False)

    fest = db.relationship(
        "Festival",
        foreign_keys=fest_id,
        backref=backref("Performance", cascade="all,delete"),
    )  # backref ?
    band = db.relationship("Band", foreign_keys=band_id)  # backref ?
    stage = db.relationship("Stage", foreign_keys=stage_id)  # backref ?

    def __repr__(self):
        return f"Performance {self.perf_id}: festival_id: {self.fest_id}; stage_id: {self.stage_id}; band_id: {self.band_id}"


class BaseUser:
    @classmethod
    def reserve_ticket(cls, form, fest_id):
        blocker = Ticket.query.filter_by(
            user_email=form.user_email.data, approved=0
        ).count()
        if blocker > 3:
            raise ValueError(
                """
                You have already issued the maximum reservations for this festival,
                please pay for part of the reservations, or contact us to cancel your reservation."""
            )
        ticket = Ticket(
            user_email=form.user_email.data,
            name=form.user_name.data,
            surname=form.user_surname.data,
            fest_id=fest_id,
        )
        db.session.add(ticket)
        fest = Festival.query.filter_by(fest_id=fest_id).first()
        if fest.current_ticket_count != fest.max_capacity:
            fest.current_ticket_count += 1
        else:
            db.session.commit()
            raise ValueError("Festival is already out of tickets")
        db.session.commit()

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
    active = Column("active", Boolean, default=True)

    __mapper_args__ = {"polymorphic_identity": 4, "polymorphic_on": perms}
    _is_authenticated = True
    _is_active = True
    _is_anonymous = False

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
        blocker = Ticket.query.filter_by(
            fest_id=fest_id, user_id=self.user_id, approved=0
        ).count()
        if blocker > 5:
            raise ValueError(
                """You have already issued the maximum reservations for this festival,
                   please pay for part of the reservations, or cancel it."""
            )
        ticket = Ticket(
            user_id=self.user_id, fest_id=fest_id, name=self.name, surname=self.surname
        )
        db.session.add(ticket)
        fest = Festival.query.filter_by(fest_id=fest_id).first()
        if fest.current_ticket_count != fest.max_capacity:
            fest.current_ticket_count += 1
        else:
            raise ValueError("Festival is already out of tickets")
        db.session.commit()

    def cancel_ticket(self, ticket_id):
        today = datetime.now()
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        if ticket.approved == 0 and today < ticket.fest.time_to:
            ticket.fest.current_ticket_count -= 1
            ticket.approved = 2
            ticket.reason = f"Canceled by {self.user_email}"
            db.session.commit()

    def get_tickets(self):
        today = datetime.now()
        actual_tickets, outdated_tickets = [], []
        tickets = Ticket.query.filter_by(user_id=self.user_id).all()
        tickets.sort(key=lambda ticket: ticket.fest.time_from)
        for ticket in tickets:
            if ticket.fest.time_from >= today:
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

    def get_all_tickets(self, fest_id=None, user_id=None):
        if fest_id is not None and user_id is not None:
            return Ticket.query.filter(fest_id == fest_id, user_id == user_id)
        elif fest_id is not None:
            return Ticket.query.filter_by(fest_id=fest_id)
        elif user_id is not None:
            return Ticket.query.filter_by(user_id=user_id)
        else:
            return Ticket.query.all()

    def get_festivals(self):
        today = datetime.today()
        actual_fests, outdated_fests = [], []

        sellers_fests = [
            f[0]
            for f in SellersList.query.with_entities(SellersList.fest_id).filter_by(
                seller_id=self.seller_id
            )
        ]
        fests = Festival.query.filter(
            or_(Festival.fest_id.in_(sellers_fests), Festival.org_id == self.user_id)
        ).all()

        fests.sort(key=lambda fest: fest.time_from)

        for fest in fests:
            if fest.time_from >= today:
                actual_fests.append(fest)
            else:
                outdated_fests.append(fest)
        return (actual_fests, outdated_fests)

    def get_sellers_tickets(self, fest_id):
        tickets = Ticket.query.filter_by(fest_id=fest_id).all()
        return tickets

    def manage_ticket_seller(self, ticket_id, action, reason):
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        today = datetime.now()
        if action == "approve" and ticket.approved == 0 and today < ticket.fest.time_to:
            ticket.approved = 1
            if reason == "":
                ticket.reason = f"Approved by {self.user_email}"
            else:
                ticket.reason = reason
        elif (
            action == "cancel" and ticket.approved == 0 and today < ticket.fest.time_to
        ):
            ticket.fest.current_ticket_count -= 1
            ticket.approved = 2
            if reason == "":
                ticket.reason = f"Cancelled by {self.user_email}"
            else:
                ticket.reason = reason
        db.session.commit()


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

    def get_sellers(self, fest_id=None):
        if fest_id is not None:
            return [row for row in SellersList.query.filter_by(fest_id=fest_id).all()]
        return [row for row in Seller.query.all()]

    def create_seller(self, form, fest_id=None):
        seller = Seller(
            user_email=form.get("email"),
            name=form.get("name"),
            surname=form.get("surname"),
            perms=3,
            passwd=generate_password_hash(form.get("password"), method="sha256"),
            address=form.get("address"),
            avatar=None,
        )
        db.session.add(seller)
        db.session.commit()
        return self.fest_add_seller({"seller_id": seller.seller_id}, fest_id)

    def fest_add_seller(self, form, fest_id):
        seller_id = form.get("seller_id")
        seller = Seller.query.filter_by(seller_id=seller_id).first()
        if seller is None:
            return (f"Seller with ID {seller_id} does nox exist.", "info")

        new_seller_list = SellersList(fest_id=fest_id, seller_id=seller_id)
        db.session.add(new_seller_list)
        db.session.commit()

        return (
            f"Seller {seller_id} successfully added to festival {fest_id}",
            "success",
        )

    def fest_del_seller(self, fest_id, seller_id):
        seller = SellersList.query.filter(
            SellersList.fest_id == fest_id, SellersList.seller_id == seller_id
        ).first()
        db.session.delete(seller)
        db.session.commit()

    def get_all_festivals(self, fest_id=None):
        if fest_id:
            return Festival.query.filter_by(fest_id=fest_id).first()
        return [row for row in Festival.query.all()]

    def add_fest(self, form):
        fest = Festival(
            fest_name=form["fest_name"].data,
            fest_logo=form["fest_logo"].data,
            description=form["fest_description"].data,
            style=form["fest_style"].data,
            cost=form["fest_cost"].data,
            time_from=form["fest_time_from"].data,
            time_to=form["fest_time_to"].data,
            address=form["fest_address"].data,
            max_capacity=form["fest_max_capacity"].data,
            age_restriction=form["fest_age_restriction"].data,
            sale=form["fest_sale"].data,
            org_id=form["fest_org_id"].data,
            status=form["fest_status"].data,
        )
        db.session.add(fest)
        db.session.commit()
        return fest.fest_id

    def cancel_fest(self, fest_id):
        fest = Festival.query.filter_by(fest_id=fest_id).first()
        db.session.delete(fest)
        db.session.commit()

    def get_perf(self, fest_id=None):
        if fest_id:
            return [row for row in Performance.query.filter_by(fest_id=fest_id).all()]
        return [row for row in Performance.query.all()]

    def fest_del_perf(self, perf_id):
        perf = Performance.query.filter_by(perf_id=perf_id).first()
        perf.canceled = True
        db.session.commit()

    def get_bands(self, fest_id=None, stage_id=None, perf_id=None):
        if fest_id is not None:
            perfs = Performance.query.filter_by(fest_id=fest_id).all()
            return [row.band for row in perfs]

        return [row for row in Band.query.all()]

    def add_band(self, form):
        band = Band(
            name=form.band_name.data,
            logo=form.band_logo.data,
            scores=form.band_scores.data,
            genre=form.band_genre.data,
            tags=form.band_tags.data,
        )
        db.session.add(band)
        db.session.commit()

    def fest_add_perf(self, form, fest_id):
        band = Band.query.filter_by(name=form["band_name"]).first()
        if band is None:
            print(f"No band with this name: {form['band_name']}")
            return (f"No band with this name: {form['band_name']}", "waring")
        try:
            stage_id = int(form["stage_id"])
        except ValueError:
            print(f"Please, provide ID for stage ID")

            return (f"Please, provide ID for stage ID", "waring")

        stage = Stage.query.filter_by(stage_id=stage_id).first()
        if stage is None:
            print(f"Now stage with this ID: {form['stage_id']}")
            return (f"Now stage with this ID: {form['stage_id']}", "warning")

        fest = Festival.query.filter_by(fest_id=fest_id).first()
        datetime_from = f"{form['date_from']} {form['time_from']}"
        datetime_to = f"{form['date_to']} {form['time_to']}"
        # Time for performance is not between festival start and end
        if not (
            fest.time_from < datetime.strptime(datetime_from, "%Y-%m-%d %H:%M")
            and fest.time_to > datetime.strptime(datetime_from, "%Y-%m-%d %H:%M")
            and fest.time_from < datetime.strptime(datetime_to, "%Y-%m-%d %H:%M")
            and fest.time_to > datetime.strptime(datetime_to, "%Y-%m-%d %H:%M")
            and datetime.strptime(datetime_to, "%Y-%m-%d %H:%M")
            > datetime.strptime(datetime_from, "%Y-%m-%d %H:%M")
        ):
            print(
                f"Date of performance is out of festival dates: {datetime_from} - {datetime_to}"
            )
            return (
                f"Date of performance is out of festival dates: {datetime_from} - {datetime_to}",
                "warning",
            )

        print(datetime.strptime(datetime_from, "%Y-%m-%d %H:%M"))
        # Find collisions with other performances
        collisions = Performance.query.filter(
            Performance.stage_id == stage.stage_id,
            or_(
                and_(
                    Performance.time_from
                    < datetime.strptime(datetime_from, "%Y-%m-%d %H:%M"),
                    Performance.time_to
                    > datetime.strptime(datetime_from, "%Y-%m-%d %H:%M"),
                ),
                and_(
                    Performance.time_from
                    < datetime.strptime(datetime_to, "%Y-%m-%d %H:%M"),
                    Performance.time_to
                    > datetime.strptime(datetime_to, "%Y-%m-%d %H:%M"),
                ),
                and_(
                    datetime.strptime(datetime_from, "%Y-%m-%d %H:%M")
                    < Performance.time_from,
                    datetime.strptime(datetime_to, "%Y-%m-%d %H:%M")
                    > Performance.time_to,
                ),
            ),
        ).all()
        if collisions:
            ids = ", ".join([str(perf.perf_id) for perf in collisions])
            print(f"There is collisions with other performances: {ids}")
            return (f"There is collisions with other performances: {ids}", "warning")
        perf = Performance(
            stage_id=stage.stage_id,
            band_id=band.band_id,
            fest_id=fest_id,
            time_from=datetime_from,
            time_to=datetime_to,
        )
        db.session.add(perf)
        db.session.commit()
        print(
            f"Performance {perf.perf_id}: Band {band.name} add to stage {stage.stage_id}"
        )
        return (
            f"Performance {perf.perf_id}: Band {band.name} add to stage {stage.stage_id}",
            "success",
        )

    def delete_band(self, band_id):
        band = Band.query.filter_by(band_id=band_id).first()
        band.deleted_on = datetime.now().strftime("%x %X")

        all_perfs = Performance.query.filter_by(band_id=band_id)
        for perf in all_perfs:
            perf.canceled = True
        db.session.commit()


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

    def remove_user(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        user.active = False
        db.session.commit()
        return (f"User {user_id} is removed", "success")

    def get_all_users(self):
        organizers = User.query.filter_by(perms=2).all()
        sellers = User.query.filter_by(perms=3).all()
        users = User.query.filter_by(perms=4).all()
        return [users, sellers, organizers]


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

    def get_all_users(self):
        admins = User.query.filter_by(perms=1).all()
        tmp = Admin.get_all_users(self) + [admins]
        return tmp

    def add_admin(self, form):
        admin = Admin.query.filter_by(user_email=form.get("email")).first()
        if admin is None:
            admin = Admin(
                name=form.get("name"),
                surname=form.get("surname"),
                user_email=form.get("email"),
                passwd=generate_password_hash(form.get("password")),
                perms=1,
                address=form.get("address"),
            )
            db.session.add(admin)
            db.session.commit()
            return (f"Admin {admin.admin_id} added to system", "success")
        return (f"Admin with email {form.get('email')} is already exists", "success")


class Ticket(db.Model):
    """Representation of ticket on festival

    Attributes:
        ticket_id (int): unique ID of ticket
        approved (int): represents if given ticket is approved - 1 / not - 0 / cancelled - 2
        reason (string): reason of cancelation
        user_email (string): used for ticket reservation for an unothorized user
        name (string): name of person
        surname (string): surname of person
        user_id (int): ID of user, that bought this ticket
        fest_id (int): festival ID ticket corresponds to
    """

    __tablename__ = "Ticket"
    ticket_id = db.Column("ticket_id", db.Integer, primary_key=True)
    user_email = Column("user_email", Text, nullable=True)
    name = Column("name", String(20), nullable=False)
    surname = Column("surname", String(20), nullable=False)

    user_id = db.Column(
        "user_id", Integer, db.ForeignKey("User.user_id"), nullable=True
    )
    fest_id = db.Column(
        "fest_id", Integer, db.ForeignKey("Festival.fest_id"), nullable=False
    )
    approved = Column("approved", Integer, nullable=False, default=0)
    reason = Column("reason", String(50))

    user = db.relationship("User", foreign_keys=user_id)
    fest = db.relationship(
        "Festival",
        foreign_keys=fest_id,
        backref=backref("Ticket", cascade="all,delete"),
    )

    def __repr__(self):
        return f"Ticket {self.ticket_id}: user_id: {self.user_id}; festival_id: {self.fest_id}"


class SellersList(db.Model):
    __tablename__ = "SellerList"
    entry_id = Column("entry_id", Integer, primary_key=True)
    fest_id = Column("fest_id", Integer, ForeignKey("Festival.fest_id"), nullable=False)
    seller_id = Column(
        "seller_id", Integer, ForeignKey("Seller.seller_id"), nullable=False
    )

    fest = relationship(
        "Festival",
        foreign_keys=fest_id,
        backref=backref("SellerList", cascade="all,delete"),
    )
    seller = relationship("Seller", foreign_keys=seller_id)

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
