class Ticket:
    pass


class User:
    """
    Basic unauthorized user 
    """

    perms = 5

    def buy_ticket(self):
        pass

    def register_fest(self):
        pass


class AuthUser(User):
    """
    Basic authorized user 
    """

    perms = 4


class Seller(AuthUser):
    perms = 3


class Organizer(Seller):
    perms = 2


class Admin(Organizer):
    perms = 1


class RootAdmin(Organizer):
    perms = 0
