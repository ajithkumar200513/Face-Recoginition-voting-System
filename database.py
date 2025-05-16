import sqlite3
from flask import g

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
    
    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.db_file)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    def create_tables(self):
        db = self.get_db()
        cursor = db.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            aadhar TEXT UNIQUE NOT NULL,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            party TEXT NOT NULL,
            constituency TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            vote_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
        ''')
        
        db.commit()
    
    def add_user(self, name, aadhar):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (name, aadhar) VALUES (?, ?)', (name, aadhar))
        db.commit()
        return cursor.lastrowid
    
    def get_user(self, user_id):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()
    
    def get_user_by_aadhar(self, aadhar):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE aadhar = ?', (aadhar,))
        return cursor.fetchone()
    
    def has_voted(self, user_id):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM votes WHERE user_id = ?', (user_id,))
        return cursor.fetchone()[0] > 0
    
    def record_vote(self, user_id, candidate_id):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO votes (user_id, candidate_id) VALUES (?, ?)', 
                      (user_id, candidate_id))
        db.commit()
    
    def get_candidates(self):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM candidates')
        return cursor.fetchall()
    
    def get_total_votes(self):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM votes')
        return cursor.fetchone()[0]
    
    def get_candidate_stats(self):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('''
        SELECT c.id, c.name, c.party, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
        ORDER BY vote_count DESC
        ''')
        return cursor.fetchall()
    
    def get_demographic_stats(self):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('''
        SELECT strftime('%H', vote_time) as hour, COUNT(*) as vote_count
        FROM votes
        GROUP BY hour
        ORDER BY hour
        ''')
        return cursor.fetchall()