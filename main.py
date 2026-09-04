import os
import flet as ft
from mic_listener import MobileMicListener
from src import npc_brain


def main(page: ft.Page):
    page.title = "M&M Voice Interface Dashboard"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 1. State Variables
    active_session = 1
    active_npc = 1

    # 2. UI Layout Components
    status_text = ft.Text("System Standby. Tap Mic to Talk.", size=16, weight=ft.FontWeight.BOLD)
    transcription_text = ft.Text("", size=14, italic=True)
    npc_response_text = ft.Text("", size=16, color=ft.Colors.BLUE_ACCENT)

    # 3. Audio Player Component (Native Flet hardware hook!)
    audio_player = ft.Audio(autoplay=True, volume=1.0)
    page.overlay.append(audio_player)

    # 4. Handle Voice Processing Results
    def process_voice_input(recorded_file_path):
        if not recorded_file_path:
            status_text.value = "Silence detected. Try again."
            page.update()
            return

        status_text.value = "Thinking..."
        transcription_text.value = "[Audio captured successfully]"
        page.update()

        try:
            # Send context directly to your database-backed narrative memory system!
            # (We pass placeholder text for now since speech_recognition is deactivated)
            mock_player_question = "Hello there! Who are you?"
            transcription_text.value = f"You said: '{mock_player_question}'"

            # Fetch response from your local SQLite db (npc_brain.py)
            npc_reply_text = npc_brain.get_npc_response_with_memory(active_session, active_npc, mock_player_question)
            npc_response_text.value = f"NPC: {npc_reply_text}"

            # If your brain returns a path to a vocal wave response, play it natively!
            # audio_player.src = "path_to_output_vocal.wav"
            # audio_player.update()
            # audio_player.play()

        except Exception as ex:
            npc_response_text.value = f"Brain Processing Warning: {ex}"

        status_text.value = "System Standby."
        page.update()

    # 5. Initialize the Mobile Mic Framework Hook
    mic_engine = MobileMicListener(page, on_result_callback=process_voice_input)

    # 6. Mic Button Click Controls
    def handle_mic_toggle(e):
        if mic_button.icon == ft.Icons.MIC:
            mic_button.icon = ft.Icons.STOP
            mic_button.icon_color = ft.Colors.RED
            status_text.value = "🎙️ Listening... Tap again to send."
            page.update()
            mic_engine.start_listening()
        else:
            mic_button.icon = ft.Icons.MIC
            mic_button.icon_color = ft.Colors.BLUE
            status_text.value = "Processing audio chunk..."
            page.update()
            mic_engine.stop_listening()

    mic_button = ft.IconButton(
        icon=ft.Icons.MIC,
        icon_color=ft.Colors.BLUE,
        icon_size=64,
        on_click=handle_mic_toggle
    )

    # 7. Render UI Components to the Mobile Screen Canvas
    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        status_text,
                        mic_button,
                        transcription_text,
                        ft.Divider(),
                        npc_response_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=30,
                width=350
            )
        )
    )


ft.app(target=main)
