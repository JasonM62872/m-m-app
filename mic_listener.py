import sys

# Trick the speech recognition tool into using the 3.14 compatible audio patch
try:
    import pyaudiowpatch as pyaudio

    sys.modules['pyaudio'] = pyaudio
except ImportError:
    pass

import speech_recognition as sr
import npc_brain


def listen_to_player():
    """Activates the microphone with hard timeouts to eliminate thread freezing loops."""
    recognizer = sr.Recognizer()

    # ANTI-CHOP ADJUSTMENTS
    recognizer.pause_threshold = 2.0
    recognizer.phrase_threshold = 0.5

    try:
        # TWEAK 1: Forces the subsystem to explicitly target your default system recording device
        with sr.Microphone() as source:
            print("\n📢 [MICROPHONE ACTIVE] Tuning audio stream...")

            # TWEAK 2: Shrunk calibration window from 1.5s down to a rapid 0.3s snippet.
            # This stops the background ambient filter from hanging indefinitely on ambient hums!
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            print(">>> START SPEAKING NOW! Talk to the NPC...")

            # TWEAK 3: Reduced timeout bounds so Python actively cuts off and drops the stream
            # if your audio drivers freeze up or if nobody talks within 7 seconds.
            audio_data = recognizer.listen(source, timeout=7, phrase_time_limit=12)
            print("[Processing voice inputs...]")

        # Send audio over to Google servers to compile text transcription
        player_text = recognizer.recognize_google(audio_data)
        print(f"The system heard: '{player_text}'")
        return player_text

    except sr.WaitTimeoutError:
        print("[System Status] Silence detected. Microphone loop closed automatically.")
        return None
    except Exception as e:
        # Catch-all print function to reveal any invisible driver complaints instantly
        print(f"[Hardware Warning] Microphone driver block encountered: {e}")
        return None


if __name__ == "__main__":
    active_session = 1
    active_npc = 1

    spoken_question = listen_to_player()
    if spoken_question:
        npc_brain.get_npc_response_with_memory(active_session, active_npc, spoken_question)
