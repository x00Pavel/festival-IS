class User:
    perms = 5


class AuthUser(User):
    perms = 4


class Seller(AuthUser):
    perms = 3


class Organizer(Seller):
    perms = 2


class Admin(Organizer):
    perms = 1


class RootAdmin(Organizer):
    perms = 0

    def __init__(self):
