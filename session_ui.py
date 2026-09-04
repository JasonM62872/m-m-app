import sqlite3
import threading  # NEW: Fixes the freezing block so the text line updates instantly
import flet as ft
import mic_listener
from src import npc_brain


def main(page: ft.Page):
    page.title = "D&D Live Session Dashboard"
    page.window_width = 450
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK

    active_session_id = 1

    def show_toast(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def load_npc_options():
        connection = sqlite3.connect("dnd_campaign.db")
        cursor = connection.cursor()
        cursor.execute("SELECT npc_id, name FROM npcs")
        rows = cursor.fetchall()
        connection.close()
        return [ft.dropdown.Option(key=str(row[0]), text=str(row[1])) for row in rows]

    def refresh_chat_display():
        chat_box.controls.clear()

        connection = sqlite3.connect("dnd_campaign.db")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT d.speaker_type, n.name, d.text_content 
            FROM dialogue d
            LEFT JOIN npcs n ON d.npc_id = n.npc_id
            WHERE d.session_id = ?
            ORDER BY d.dialogue_id DESC
        """, (active_session_id,))
        logs = cursor.fetchall()
        connection.close()

        for speaker_type, npc_name, text in logs:
            if speaker_type == "player":
                chat_box.controls.append(
                    ft.Container(
                        content=ft.Text(f"🎤 Players: {text}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_GREY_800,
                        padding=12,
                        border_radius=10,
                        alignment=ft.Alignment(1, 0),
                        margin=5
                    )
                )
            else:
                chat_box.controls.append(
                    ft.Container(
                        content=ft.Text(f"🎭 {npc_name}: {text}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.AMBER_900,
                        padding=12,
                        border_radius=10,
                        alignment=ft.Alignment(-1, 0),
                        margin=5
                    )
                )
        page.update()

    # This background task handles the mic processing so the main UI never freezes
    def background_mic_task(npc_id):
        # 1. Run our functional background microphone reader script
        spoken_text = mic_listener.listen_to_player()

        # Reset the alert warning text line once audio capturing finishes
        status_text.value = "Idle - Waiting for activation"
        status_text.color = ft.Colors.GREY_500
        mic_button.disabled = False  # Re-enable the button
        page.update()

        if not spoken_text:
            show_toast("Microphone timeout or silent input.", ft.Colors.RED)
            return

        refresh_chat_display()

        # 2. Fire up the voice generator pipeline script
        npc_brain.get_npc_response_with_memory(active_session_id, npc_id, spoken_text)

        # 3. Pull newest AI message logs onto the UI display canvas
        refresh_chat_display()

    def trigger_microphone(e):
        npc_id_str = npc_selector.value
        if not npc_id_str:
            show_toast("Error: Select an active NPC character first!", ft.Colors.RED)
            return

        npc_id = int(npc_id_str)

        # FIX: The visual text changes instantly and the button disables so you can't double-click it
        status_text.value = ">>> 📢 SPEAK NOW! Talk to the NPC... <<<"
        status_text.color = ft.Colors.GREEN
        mic_button.disabled = True
        page.update()

        # FIX: Spin up a side background engine thread to listen to the microphone hardware
        threading.Thread(target=background_mic_task, args=(npc_id,), daemon=True).start()

    # --- UI LAYOUT COMPONENTS ---

    header = ft.Container(
        content=ft.Column([
            ft.Text("⚔️ Session Dashboard", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
        ]),
        padding=5
    )

    npc_selector = ft.Dropdown(
        label="Active Speaking NPC",
        border_color=ft.Colors.AMBER_400,
        options=load_npc_options(),
        width=350,
    )

    status_text = ft.Text("Idle - Waiting for activation", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500)

    chat_box = ft.Column(scroll=ft.ScrollMode.AUTO, height=280, width=350)

    mic_button = ft.Button(
        content=ft.Row(
            [ft.Icon(ft.Icons.MIC, color=ft.Colors.BLACK),
             ft.Text("Listen to Players", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor=ft.Colors.AMBER_400,
        width=350,
        height=55,
        on_click=trigger_microphone
    )

    page.add(
        ft.Container(
            content=ft.Column([
                header,
                ft.Container(content=npc_selector, padding=5),
                ft.Container(content=status_text, padding=5),
                ft.Text("📜 Campaign Dialogue Log (Newest Top)", size=12, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_500),
                ft.Container(
                    content=chat_box,
                    padding=5,
                    border=ft.Border(
                        top=ft.BorderSide(1, ft.Colors.GREY_800),
                        bottom=ft.BorderSide(1, ft.Colors.GREY_800),
                        left=ft.BorderSide(1, ft.Colors.GREY_800),
                        right=ft.BorderSide(1, ft.Colors.GREY_800)
                    ),
                    border_radius=10,
                    bgcolor=ft.Colors.BLACK
                ),
                ft.Container(content=mic_button, padding=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=5
        )
    )

    refresh_chat_display()


if __name__ == "__main__":
    ft.run(main)
