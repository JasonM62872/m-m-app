import sqlite3

def initialize_database():
    """Creates the database file and all required tables for the D&D app."""
    # This automatically creates a file named 'dnd_campaign.db' in your project folder
    connection = sqlite3.connect("dnd_campaign.db")
    cursor = connection.cursor()

    print("Creating tables in the sandbox database...")

    # 1. CREATE SESSIONS TABLE (Tracks different game nights)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT CURRENT_TIMESTAMP,
        campaign_name TEXT NOT NULL
    );
    """)

    # 2. CREATE NPCS TABLE (Stores character profiles)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS npcs (
        npc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        voice_id TEXT,
        personality_prompt TEXT NOT NULL
    );
    """)

    # 3. CREATE DIALOGUE TABLE (Stores the actual chat logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dialogue (
        dialogue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        npc_id INTEGER,
        speaker_type TEXT NOT NULL, -- 'player' or 'npc'
        text_content TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (session_id),
        FOREIGN KEY (npc_id) REFERENCES npcs (npc_id)
    );
    """)

    # Commit the changes and close the connection safely
    connection.commit()
    connection.close()
    print("Database tables created successfully!")

# This line tells Python to run the function when you click play
if __name__ == "__main__":
    initialize_database()
