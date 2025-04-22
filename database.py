import sqlite3
from datetime import datetime
import hashlib
import secrets

class Database:
    def __init__(self, db_name="dollar_tracker.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bills table with user reference
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face_value REAL NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                printing_location TEXT,
                series_year INTEGER,
                is_star_note BOOLEAN,
                is_star_filled BOOLEAN,
                image_path TEXT,
                estimated_value REAL,
                added_by INTEGER,
                FOREIGN KEY (added_by) REFERENCES users(id)
            )
        ''')
        self.conn.commit()
        
    def create_user(self, username, password):
        """Create a new user with hashed password"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, salt)
                VALUES (?, ?, ?)
            ''', (username, password_hash, salt))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def verify_user(self, username, password):
        """Verify user credentials"""
        self.cursor.execute('SELECT id, password_hash, salt FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        
        if not result:
            return None
            
        user_id, stored_hash, salt = result
        input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        if input_hash == stored_hash:
            return user_id
        return None
        
    def add_bill(self, face_value, serial_number, user_id, printing_location=None, 
                series_year=None, is_star_note=False, is_star_filled=False,
                image_path=None, estimated_value=None):
        try:
            self.cursor.execute('''
                INSERT INTO bills (face_value, serial_number, printing_location,
                                 series_year, is_star_note, is_star_filled,
                                 image_path, estimated_value, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (face_value, serial_number, printing_location, series_year,
                 is_star_note, is_star_filled, image_path, estimated_value, user_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def get_bill(self, serial_number):
        self.cursor.execute('''
            SELECT b.*, u.username 
            FROM bills b
            LEFT JOIN users u ON b.added_by = u.id
            WHERE b.serial_number = ?
        ''', (serial_number,))
        return self.cursor.fetchone()
        
    def search_bills(self, criteria):
        query = '''
            SELECT b.*, u.username 
            FROM bills b
            LEFT JOIN users u ON b.added_by = u.id
            WHERE 1=1
        '''
        params = []
        
        if criteria.get('face_value'):
            query += " AND b.face_value = ?"
            params.append(criteria['face_value'])
        if criteria.get('printing_location'):
            query += " AND b.printing_location LIKE ?"
            params.append(f"%{criteria['printing_location']}%")
        if criteria.get('series_year'):
            query += " AND b.series_year = ?"
            params.append(criteria['series_year'])
        if criteria.get('is_star_note') is not None:
            query += " AND b.is_star_note = ?"
            params.append(criteria['is_star_note'])
        if criteria.get('added_by'):
            query += " AND b.added_by = ?"
            params.append(criteria['added_by'])
            
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
        
    def update_bill(self, serial_number, user_id, **kwargs):
        if not kwargs:
            return False
            
        # Verify user has permission to update
        self.cursor.execute('SELECT added_by FROM bills WHERE serial_number = ?', (serial_number,))
        result = self.cursor.fetchone()
        if not result or result[0] != user_id:
            return False
            
        set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
        query = f"UPDATE bills SET {set_clause} WHERE serial_number = ?"
        
        self.cursor.execute(query, list(kwargs.values()) + [serial_number])
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def get_user_bills(self, user_id):
        """Get all bills added by a specific user"""
        self.cursor.execute('''
            SELECT b.*, u.username 
            FROM bills b
            LEFT JOIN users u ON b.added_by = u.id
            WHERE b.added_by = ?
        ''', (user_id,))
        return self.cursor.fetchall()
        
    def close(self):
        self.conn.close() 