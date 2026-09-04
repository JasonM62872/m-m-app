import sqlite3


def add_new_npc(name, voice_id, personality_prompt, faction, motivation, secrets):
    """Inserts a brand new NPC profile with custom lore slots into the database."""
    # 1. Dynamically find the folder this specific code file is currently running from
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Securely connect to the database sitting inside that exact folder path
    connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
    cursor = connection.cursor()

    sql_command = """
    INSERT INTO npcs (name, voice_id, personality_prompt, faction, motivation, secrets) 
    VALUES (?, ?, ?, ?, ?, ?);
    """
    cursor.execute(sql_command, (name, voice_id, personality_prompt, faction, motivation, secrets))
    connection.commit()
    connection.close()
    print(f"Success! {name} has been added to the database.")


def update_npc(npc_id, name, voice_id, personality_prompt, faction, motivation, secrets):
    """Updates an existing NPC's details based on their ID."""
    # 1. Dynamically find the folder this specific code file is currently running from
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Securely connect to the database sitting inside that exact folder path
    connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
    cursor = connection.cursor()

    sql_command = """
    UPDATE npcs 
    SET name=?, voice_id=?, personality_prompt=?, faction=?, motivation=?, secrets=?
    WHERE npc_id=?;
    """
    cursor.execute(sql_command, (name, voice_id, personality_prompt, faction, motivation, secrets, npc_id))
    connection.commit()
    connection.close()


def delete_npc(npc_id):
    """Safely removes an NPC and clears their history to prevent database crashes."""
    # 1. Dynamically find the folder this specific code file is currently running from
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Securely connect to the database sitting inside that exact folder path
    connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
    cursor = connection.cursor()

    try:
        # 1. Clear out any dialogue rows tying this character down
        cursor.execute("DELETE FROM dialogue WHERE npc_id = ?", (npc_id,))

        # 2. Now safely delete the actual character profile row
        cursor.execute("DELETE FROM npcs WHERE npc_id = ?", (npc_id,))

        connection.commit()
        print(f"[Database] NPC {npc_id} and all related logs successfully deleted.")
    except Exception as e:
        print(f"[Database Error] Could not delete NPC: {e}")
    finally:
        connection.close()


def clear_session_dialogue(session_id):
    """Permanently wipes the dialogue history for a specific campaign session."""
    # 1. Dynamically find the folder this specific code file is currently running from
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Securely connect to the database sitting inside that exact folder path
    connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
    cursor = connection.cursor()
    # Deletes all chat rows matching our current game session night
    cursor.execute("DELETE FROM dialogue WHERE session_id = ?", (session_id,))
    connection.commit()
    connection.close()
    print(f"Session {session_id} dialogue history cleared.")
