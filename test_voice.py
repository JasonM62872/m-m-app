import os
import sqlite3

# Find your exact active mobile project directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "dnd_campaign.db")

print("Initializing campaign database migration script...")

if not os.path.exists(db_path):
    print(f"❌ ERROR: Missing database file at {db_path}")
else:
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # 1. Fetch all current characters to inspect their old voice layouts
        cursor.execute("SELECT npc_id, name, voice_id FROM npcs")
        characters = cursor.fetchall()

        print(f"Found {len(characters)} characters to update.")

        for npc_id, name, old_voice in characters:
            # 2. Determine the best matching local fantasy short-code translation
            # We map their old desktop voices to your 10 new offline archetypes!
            new_voice = "am_adam"  # Default safety baseline (Dwarf/Goblin)

            # Simple conversion rule: if it was an old female voice marker, switch to Elf female
            if old_voice in ["1", "female", "nova", "shimmer", "alloy"]:
                new_voice = "af_bella"
            elif old_voice in ["0", "male", "echo", "onyx"]:
                new_voice = "am_echo"  # Force old male voices to booming Orc!

            # If the character's name is Gor, let's explicitly lock him into his Orc voice!
            if "gor" in name.lower():
                new_voice = "am_echo"

            # 3. Permanently write the new mobile short-code string into the database row
            cursor.execute("UPDATE npcs SET voice_id = ? WHERE npc_id = ?", (new_voice, npc_id))
            print(f" ➔ Updated {name}: Old Voice '{old_voice}' converted to Offline Archetype '{new_voice}'")

        connection.commit()
        connection.close()
        print("🎉 DATABASE MIGRATION COMPLETE! All characters have been migrated to the offline asset vault.")

    except Exception as e:
        print(f"❌ Migration block failure: {e}")
