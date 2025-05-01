import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self, db_path='data/emotions.db'):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
           
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    designation TEXT NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
          
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotion_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES users (employee_id)
                )
            ''')
            
           
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audio_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES users (employee_id)
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Failed to initialize database: {str(e)}")
        finally:
            if conn:
                conn.close()

    def add_user(self, employee_id, name, designation, password):
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (employee_id, name, designation, password)
                VALUES (?, ?, ?, ?)
            ''', (employee_id, name, designation, password))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Registration Error", "Employee ID already exists")
            return False
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Failed to add user: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def authenticate_user(self, employee_id, password):
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT employee_id, name, designation FROM users
                WHERE employee_id = ? AND password = ?
            ''', (employee_id, password))
            
            user = cursor.fetchone()
            return user if user else None
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Failed to authenticate user: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def log_emotion(self, employee_id, emotion, confidence):
        """Log an emotion detection result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO emotion_logs (employee_id, emotion, confidence)
                VALUES (?, ?, ?)
            ''', (employee_id, emotion, confidence))
            
            conn.commit()
            
           
            self._check_negative_emotions(employee_id)
        except sqlite3.Error as e:
            print(f"Failed to log emotion: {str(e)}")  
        finally:
            if conn:
                conn.close()

    def _check_negative_emotions(self, employee_id):
        """Check if employee has frequent negative emotions today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM emotion_logs
                WHERE employee_id = ? AND emotion IN ('sad', 'angry', 'fear')
                AND date(timestamp) = date('now')
            ''', (employee_id,))
            
            negative_count = cursor.fetchone()[0]
            
            if negative_count >= 5: 
                cursor.execute('SELECT name FROM users WHERE employee_id = ?', (employee_id,))
                name = cursor.fetchone()[0]
                return name
            return None
        except sqlite3.Error:
            return None
        finally:
            if conn:
                conn.close()

    def get_employee_emotion_stats(self, employee_id, days=7):
        """Get emotion statistics for an employee"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT emotion, COUNT(*) as count, date(timestamp) as day
                FROM emotion_logs
                WHERE employee_id = ? AND date(timestamp) >= date('now', ?)
                GROUP BY emotion, day
                ORDER BY day
            ''', (employee_id, f'-{days} days'))
            
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Failed to get emotion stats: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    def get_all_emotion_stats(self, days=7):
        """Get emotion statistics for all employees"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
          
            cursor.execute('''
                SELECT emotion, COUNT(*) as count
                FROM emotion_logs
                WHERE date(timestamp) >= date('now', ?)
                GROUP BY emotion
            ''', (f'-{days} days',))
            
            overall_stats = cursor.fetchall()
            
           
            cursor.execute('''
                SELECT u.employee_id, u.name, u.designation, e.emotion, COUNT(*) as count
                FROM emotion_logs e
                JOIN users u ON e.employee_id = u.employee_id
                WHERE e.emotion IN ('sad', 'angry', 'fear')
                AND date(e.timestamp) >= date('now', ?)
                GROUP BY u.employee_id, e.emotion
                HAVING COUNT(*) >= 3
                ORDER BY count DESC
            ''', (f'-{days} days',))
            
            negative_stats = cursor.fetchall()
            
            return overall_stats, negative_stats
        except sqlite3.Error as e:
            print(f"Failed to get all emotion stats: {str(e)}")
            return [], []
        finally:
            if conn:
                conn.close()