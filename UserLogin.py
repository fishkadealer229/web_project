from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, username, db):
        self.__user = db.getUser(username)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['username'])
