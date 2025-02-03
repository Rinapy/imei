import sqlite3
from protocols.repository import DataBaseRepository
from utils.token_gen import generate_jwt
from utils.token_gen import decode_jwt

class SQLiteDataBaseRepository(DataBaseRepository):
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                permission_level INTEGER NOT NULL DEFAULT 0,
                token TEXT
            )
        ''')
        self.conn.commit()

    def get_user_token(self, user_id: int) -> bool | str:
        cursor = self.conn.cursor()
        cursor.execute('SELECT token FROM users WHERE tg_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
        
        if result[0]:
            try:
                decoded = decode_jwt(result[0])
                print(decoded)
                if not isinstance(decoded, str):
                    return result[0]
            except:
                token = generate_jwt(user_id, "telegram")
                cursor.execute(
                    'UPDATE users SET token = ? WHERE tg_id = ?',
                    (token, user_id)
                )
                self.conn.commit()
                return token
        
        token = generate_jwt(user_id, "telegram")
        cursor.execute(
            'UPDATE users SET token = ? WHERE tg_id = ?',
            (token, user_id)
        )
        self.conn.commit()
        return token

    def add_user_in_wl(self, user_id: int) -> bool | int:
        cursor = self.conn.cursor()
        # Сначала проверяем существование пользователя
        cursor.execute('SELECT permission_level FROM users WHERE tg_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False  # Пользователь не существует
            
        if result[0] == 1:
            return 1  # Пользователь уже в белом списке
            
        # Обновляем права доступа
        cursor.execute(
            'UPDATE users SET permission_level = ? WHERE tg_id = ?',
            (1, user_id)
        )
        self.conn.commit()
        return True  # Успешно добавили в белый список

    def del_user_in_wl(self, user_id: int) -> bool | int:
        cursor = self.conn.cursor()
        # Сначала проверяем существование пользователя
        cursor.execute('SELECT permission_level FROM users WHERE tg_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False  # Пользователь не существует
            
        if result[0] == 0:
            return 0  # Пользователь не белом списке
            
        # Обновляем права доступа
        cursor.execute(
            'UPDATE users SET permission_level = ? WHERE tg_id = ?',
            (0, user_id)
        )
        self.conn.commit()
        return True  # Успешно убрали из белого списока

    def get_user(self, user_id: int) -> bool | int:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT permission_level FROM users WHERE tg_id = ?',
            (user_id,)  # Кортеж с одним элементом должен иметь запятую
        )
        result = cursor.fetchone()
        
        if not result:
            return False  # Пользователь не найден
        
        return result[0]  # Возвращаем permission_level

    def add_user(self, user_id: int) -> bool:
        cursor = self.conn.cursor()
        try:
            token = generate_jwt(user_id, "telegram")  # Генерируем токен до вставки
            cursor.execute(
                'INSERT INTO users (tg_id, permission_level, token) VALUES (?, ?, ?)',
                (user_id, 0, token)  # Сразу добавляем и токен
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return True  # Пользователь уже существует
        except Exception:
            return False

    def __del__(self):
        self.conn.close() 