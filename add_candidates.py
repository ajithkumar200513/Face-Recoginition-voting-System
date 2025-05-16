import sqlite3

def add_sample_candidates():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    
    # Clear existing candidates (optional)
    cursor.execute("DELETE FROM candidates")
    
    # Add 5 sample candidates
    candidates = [
        ("Rahul Sharma", "Bharatiya Janata Party", "Mumbai North"),
        ("Priya Patel", "Indian National Congress", "Delhi South"), 
        ("Amit Kumar", "Aam Aadmi Party", "Bangalore Central"),
        ("Neha Gupta", "Shiv Sena", "Pune West"),
        ("Sanjay Singh", "All India Trinamool Congress", "Kolkata North")
    ]
    
    cursor.executemany(
        "INSERT INTO candidates (name, party, constituency) VALUES (?, ?, ?)",
        candidates
    )
    
    conn.commit()
    print("Added 5 sample candidates successfully")
    conn.close()

if __name__ == "__main__":
    add_sample_candidates()