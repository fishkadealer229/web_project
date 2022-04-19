import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addUser(self, name, username, password):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE username LIKE '{username}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким username уже существует")
                return False

            self.__cur.execute("INSERT INTO users (name, username, password) VALUES(?, ?, ?)",
                               (name, username, password,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    def getUser(self, username_):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE username = '{username_}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False
