import os
import sys        # 🌟 FIXED: Added this crucial module!
import time
import random
import sqlite3
import requests
import pygame
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================================
# 🌟 STEP 1: MOBILE PATH COMPATIBILITY ROUTINE
# =========================================================================
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # When running as a compiled Google Play mobile app package
    BASE_DIR = sys._MEIPASS
else:
    # When testing locally inside your Windows Desktop environment
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📁 These create stable, universal links to your file folders
DATABASE_PATH = os.path.join(BASE_DIR, "dnd_campaign.db")
MODEL_PATH = os.path.join(BASE_DIR, "assets", "kokoro-v0_19.onnx")
VOICES_PATH = os.path.join(BASE_DIR, "assets", "voices", "voices-v1.0.bin")
# =========================================================================

# Global tracking slot to prevent Windows file system locks
voice_file_track_toggle = True

def generate_offline_voice_response(npc_name, reply_text, chosen_voice_archetype, audio_player_widget=None):
    """Generates a high-quality fantasy voice file entirely offline and switches file tracks."""
    global voice_file_track_toggle

    # 1. Safety baseline fallback check
    if not chosen_voice_archetype or chosen_voice_archetype in ["None", "0", "1"]:
        print("[Safety Net Alert] Voice Archetype was blank! Defaulting to 'am_adam'.")
        chosen_voice_archetype = "am_adam"

    print(f"[Mobile Engine] Synthesizing offline voice vector code: {chosen_voice_archetype}")

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "assets", "kokoro-v0_19.onnx")
        voices_path = os.path.join(base_dir, "assets", "voices", "voices-v1.0.bin")

        # 2. Alternates file target names dynamically to bypass the OS file lock
        if voice_file_track_toggle:
            filename = "../output_1.wav"
        else:
            filename = "output_2.wav"
        voice_file_track_toggle = not voice_file_track_toggle
        output_audio_path = os.path.join(base_dir, filename)

        # 3. Optimized Multithreading Engine Initialization
        import onnxruntime as ort
        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = 4  # Locks execution onto 4 physical CPU cores
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

        # Build the session with options, then pass it using the explicit .from_session constructor
        onnx_session = ort.InferenceSession(model_path, session_options)
        onnx_engine = Kokoro.from_session(onnx_session, voices_path)

        # 4. Run synthesis matrix calculation completely offline
        samples, sample_rate = onnx_engine.create(
            text=reply_text,
            voice=chosen_voice_archetype,
            speed=1.0,
            lang="en-us"
        )

        # Write the audio waves down to the selected open file track cleanly
        sf.write(output_audio_path, samples, sample_rate)
        print(f"[Mobile Engine] Audio successfully written to: {output_audio_path}")

        # 5. Native Windows Hardware Speaker Driver
        try:
            print(f"[Native Audio Driver] Loading fresh track into sound card: {filename}")
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate)

            # Unload previous music handle to break OS file retention holds cleanly
            pygame.mixer.music.unload()
            pygame.mixer.music.load(output_audio_path)
            pygame.mixer.music.play()
            print("[Native Audio Driver] Sound waves successfully forced to speakers!")
        except Exception as audio_err:
            print(f"[Native Audio Failure] Direct hardware playback blocked: {audio_err}")

        # Keep this Flet fallback line so your smartphone layers remain intact for later
        if audio_player_widget:
            audio_player_widget.src = f"file:///{output_audio_path}".replace("\\", "/")
            try:
                audio_player_widget.update()
            except:
                pass

    except Exception as e:
        print(f"[Mobile Audio Failure] Local synthesis block: {e}")

def log_to_database(session_id, npc_name, speaker_type, text_content):
    try:
        # 🌟 UPDATED: Uses the universal mobile-ready database path variable
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO dialogue (session_id, npc_id, speaker_type, text_content)
            VALUES (?, ?, ?, ?);
        """, (session_id, npc_name, speaker_type, text_content))
        connection.commit()
        connection.close()
    except Exception as log_err:
        print(f"⚠️ [Database Log Error] Failed to write message log: {log_err}")

def get_session_interaction_count(session_id, npc_name):
    try:
        # 🌟 UPDATED: Uses the universal mobile-ready database path variable
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM dialogue
            WHERE session_id = ? AND npc_id = ? AND speaker_type = 'player'
        """, (session_id, npc_name))
        count = cursor.fetchone()
        connection.close()
        return count if count else (0,)
    except Exception as count_err:
        print(f"⚠️ [Session Count Error] Failed to read interaction numbers: {count_err}")
        return (0,)

def get_recent_chat_history(session_id, npc_name, limit=6):
    try:
        # 🌟 UPDATED: Uses the universal mobile-ready database path variable
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT speaker_type, text_content
            FROM dialogue
            WHERE session_id = ? AND npc_id = ?
            ORDER BY dialogue_id DESC
            LIMIT ?
        """, (session_id, npc_name, limit))
        rows = cursor.fetchall()
        connection.close()

        rows.reverse()
        history_messages = []
        for speaker_type, text in rows:
            role = "user" if speaker_type == "player" else "assistant"
            history_messages.append({"role": role, "content": text})
        return history_messages
    except Exception as history_err:
        print(f"⚠️ [History Fetch Error] Failed to query dialog logs: {history_err}")
        return []


def get_npc_response_with_memory(session_id, user_text, npc_name, voice_key=None, audio_player_widget=None):
    # 🌟 Path calculation happens at the top of the file globally now!

    try:
        # 1. Securely connect using your universal database path variable
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name, personality_prompt, voice_id, faction, motivation, secrets
            FROM npcs
            WHERE npc_id = ? OR name = ?
        """, (npc_name, npc_name))
        npc_data = cursor.fetchone()
        connection.close()
    except Exception as db_err:
        print(f"⚠️ [Database Sync Error] Could not query profile: {db_err}")
        return None

    if not npc_data:
        print(f"Error: NPC '{npc_name}' not found!")
        return None

    real_npc_name = npc_data[0]
    base_personality = npc_data[1]

    # 🎯 Pulls the voice string cleanly from the 3rd database slot (index 2)
    voice_style = npc_data[2]
    if not voice_style or voice_style in ["0", "1", "None"]:
        voice_style = "am_echo"

    print(f"🎯 [Database Sync] Automatically mapped voice archetype '{voice_style}' for NPC '{real_npc_name}'")

    faction = npc_data[3] if npc_data[3] else "Independent"
    motivation = npc_data[4] if npc_data[4] else "Standard behavior"
    campaign_secret = npc_data[5] if npc_data[5] else "No specific secrets known."

    # Log incoming user message text to backend narrative log
    log_to_database(session_id, real_npc_name, speaker_type="player", text_content=user_text)

    # Fetch current session tracking details
    times_asked = get_session_interaction_count(session_id, real_npc_name)[0]

    # Safe string hashing so letters like 'Gor' don't crash your randomizer!
    try:
        random.seed(hash(real_npc_name) + int(session_id))
    except ValueError:
        random.seed(hash(real_npc_name) + hash(session_id))

    reveal_threshold = random.randint(1, 3)

    if times_asked >= reveal_threshold:
        secret_directive = (
            f"CRITICAL RULES: You have decided to reveal this secret now. "
            f"Weave this information naturally into your reply: '{campaign_secret}'"
        )
    else:
        secret_directive = (
            f"CRITICAL RULES: You are keeping a secret. Do NOT reveal it yet. "
            f"The secret is: '{campaign_secret}'. Deflect the question, act suspicious, "
            f"or demand gold before you give it up."
        )
    # 🌟 NEW CONVERSATIONAL DIRECTIVE SYSTEM TEMPLATE 🌟
    # We remove the restrictive "3 short sentences" count rule which tricks the small model into infinite loops.
    master_system_prompt = (
        f"You are roleplaying as {real_npc_name}. "
        f"Personality: {base_personality}. "
        f"Faction: {faction}. "
        f"Goal: {motivation}.\n\n"
        f"{secret_directive}\n\n"
        f"CRITICAL ROLEPLAY CONSTRAINTS:\n"
        f"- Chat naturally in a concise, conversational tone.\n"
        f"- Give ONE direct answer or one brief thought.\n"
        f"- Never repeat the same phrase structure or cycle words.\n"
        f"- Keep your response short and dynamic."
    )
    # Fetch conversation log history data explicitly right here
    history_messages = get_recent_chat_history(session_id, real_npc_name, limit=6)

    # Assemble your working API history array
    api_messages = [{"role": "system", "content": master_system_prompt}]
    api_messages.extend(history_messages)
    api_messages.append({"role": "user", "content": user_text})

    print(f"[Thinking... Routing to Local Phi-3 Model | Interaction #{times_asked}]")

    try:
        # --- OLLAMA API CALL ---
        ollama_url = "http://localhost:11434/api/chat"
        payload = {
            "model": "phi3:mini",
            "messages": api_messages,
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 100,
                "temperature": 0.6,
                "repetition_penalty": 1.2,  # 🌟 NEW: Forces the AI to stop repeating itself!
                "num_thread": 4
            }
        }

        response = requests.post(ollama_url, json=payload)
        response_data = response.json()

        # Capture the true text response string cleanly!
        npc_reply_text = response_data["message"]["content"]
        print(f"\n{real_npc_name} says: {npc_reply_text}")

        # Save the real generated AI response to your database log
        log_to_database(session_id, real_npc_name, speaker_type="npc", text_content=npc_reply_text)

        # =========================================================================
        # 🌟 THE FINAL VOICE GENERATOR WIRE INJECTION 🌟
        # =========================================================================
        generate_offline_voice_response(
            npc_name=real_npc_name,
            reply_text=npc_reply_text,
            chosen_voice_archetype=voice_style,
            audio_player_widget=audio_player_widget
        )
        # =========================================================================

        # Hand the finalized text response back to main_app.py to update the UI
        return npc_reply_text

    except Exception as e:
        print(f"[Ollama Server Error] Make sure the Ollama app is actively running in your Windows tray! Error: {e}")
        return "I am feeling a bit tongue-tied traveler. Ask me again in a moment."

