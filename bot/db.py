import sqlite3


class DBBot:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def site_exists(self, user_id, site):
        result = self.cursor.execute("SELECT `id` FROM `logins` WHERE `users_id` = ? AND `site` = ?",
                                     (self.get_user_id(user_id), site))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_login(self, user_id, site, login, password):
        self.cursor.execute("INSERT INTO `logins` (`users_id`, `site`, `login`, `password`) VALUES (?, ?, ?, ?)",
                            (self.get_user_id(user_id),
                             site,
                             login,
                             password))
        return self.conn.commit()

    def del_login(self, user_id, site):
        self.cursor.execute("DELETE FROM `logins` WHERE `users_id` = ? AND `site` = ?",
                            (self.get_user_id(user_id),
                             site))
        return self.conn.commit()

    def get_info(self, user_id, site):
        res = self.cursor.execute("SELECT `login`, `password` FROM `logins` WHERE `users_id` = ? AND `site` = ?",
                                  (self.get_user_id(user_id), site,))
        return res.fetchall()

    def close(self):
        self.conn.close()
