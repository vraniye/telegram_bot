import sqlite3


class BotDB:

    def __init__(self, db_file):
        """Инициализация соеденения с БД"""
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли пользователь в ДБ"""
        result = self.cursor.execute(
            "SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Получаем id пользователя в базе по его user_id в тг"""
        result = self.cursor.execute(
            "SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем пользователя в базу данных"""
        self.cursor.execute(
            "INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_record(self, user_id, joke):
        """Добавляем анекдот в базу данных"""
        self.cursor.execute(
            "INSERT INTO `records` (`user_id`, `joke`) VALUES (?, ?)", (self.get_user_id(user_id), joke))
        return self.conn.commit()

    def add_user_to_moderation_list(self, user_id):
        """Добавляем пользователя в базу данных модераторов бота"""
        self.cursor.execute(
            "INSERT INTO `moderator_users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def user_exist_in_moderation_list(self, user_id):
        """Проверяем, есть ли пользователь в базе данных модераторов"""
        result = self.cursor.execute(
            "SELECT `id` FROM `moderator_users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_record(self):
        """Получение анекдота из БД"""
        result = self.cursor.execute(
            "SELECT `joke` FROM `records` ORDER BY RANDOM() LIMIT 1")
        return result.fetchone()[0]

    def close(self):
        """Закрытие соеденения с БД"""
        self.conn.close()
