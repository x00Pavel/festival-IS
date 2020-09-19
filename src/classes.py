class Ticket:
    """Representation of ticket on festival

    Attributes:
        ticket_id (int): unique ID of ticket
        user_id (int): user ID, that bought this ticket
        fest_id (int): festival ID ticket corresponds to        
    """

    def __init__(self, ticket_id: int, fest_id: int, user_id: int):
        """Initialisation of new ticket

        Args:
            ticket_id (int): ID for new ticket
            fest_id (int): festival ID
            user_id (int): user ID
        """
        self.ticket_id = ticket_id
        self.fest_id = fest_id
        self.user_id = user_id
        # TODO: Get festival by ID
        # self.cost = get_fest(fest).cost


class Address:
    """Representation of address for festival, users and etc. 
    """

    def __inti__(self, city: str, street: str, number: int):
        """New street

        Args:
            city (str): 
            street (str):
            number (int):
        """
        self.city = city
        self.street = street
        self.number = number


class Festival:
    """
    Reperesentation of Festival.
    """

    def __init__(
        self,
        address: int,
        time_from: int,
        time_to: int,
        fest_id: int,
        cost: int,
        capacity: int,
        age: int = 16,
        desc: str = "No description",
        style: str = "No style",
        logo: str = "No logo",
    ):
        """New festival

        Args:
            address (int): address ID, where festival is held 
            time_from (int): when festival begins (in seconds)
            time_to (int): when festival ends (in seconds)
            fest_id (int): unique ID of new festival
            cost (int): cost for ticket on festival
            capacity (int): capacity of festival (how many tickets can be soled)
            age (int, optional): age restriction for festival. Defaults to "16".
            desc (str, optional): descritpion of festival. Defaults to "No description".
            style (str, optional): style of festival. Defaults to "No style".
            logo (str, optional): link to logo of festival. Defaults to "No logo".
        """
        self.address = address
        self.time_from = time_from
        self.time_to = time_to
        self.fest_id = fest_id
        self.cost = cost
        self.capacity = capacity
        self.age = age
        self.style = style
        self.logo = logo

    # TODO: Function for downloading logo to client side or to cache ?

    # def edit_value(self, attr: str, value):
    #     # For checking if given attribute exists.
    #     # If not, AttributeError will be through
    #     # TODO: how to deal with errors? Error codes or raising exceptions?
    #     getattr(self, attr)
    #     setattr(self, attr, value)


class User:
    """
    Basic unauthorized user 
    """

    perms = 5

    def __init__(
        self, email: str, name: str, surname: str, address: id, phone_number: "str"
    ):
        """[summary]

        Args:
            email (str): unique email address of user
            name (str): 
            surname (str): 
            address (id):
            phone_number (str):
        """

        self.email = email
        self.name = name
        self.surname = surname
        self.address = address
        self.phone_number = phone_number

    def buy_ticket(self):
        pass

    def register_fest(self):
        pass


class AuthUser(User):
    """
    Basic authorized user 
    """

    perms = 4

    def get_ticket_status(self):
        pass

    def change_profile(self):
        pass


class Seller(AuthUser):
    perms = 3

    def confirm_reservation(self):
        pass


class Organizer(Seller):
    perms = 2

    def add_seller(self):
        pass

    def delete_seller(self):
        pass


class Admin(Organizer):
    perms = 1

    def add_organizer(self):
        pass

    def delete_organizer(self):
        pass


class RootAdmin(Organizer):
    """Reperesentation of root admin. Only this role can add new admins 
    """

    perms = 0

    def add_admin(self):
        pass


class Band:
    """
    Representation of music band
    """

    def __init__(
        self,
        band_name: str,
        scores: int = 0,
        perf_id: int = None,
        logo: str = "No logo",
        style: str = "No style",
        tags: [str] = ["No tags"],
    ):
        """New music band

        Args:
            band_name (str): unique name of band
            perf_id (int, optional): performance ID, where band will be play. Can be empty
                           just for adding band to databse
            scores (int, optional): [description]. Defaults to 0.
            logo (str, optional): [description]. Defaults to "No logo".
            style (str, optional): [description]. Defaults to "No style".
            tags ([type], optional): [description]. Defaults to ["No tags"].
        """
        self.band_id = band_id
        self.perf_id = perf_id
        self.scores = scores
        self.logo = logo
        self.style = style
        self.tags = tags


class BandMember:
    """Representaton of music band member 
    One member can be a member only for one band
    """

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
