import os
import sys        # 🌟 Added to scan platform deployment properties
import time
import flet as ft
import mic_listener
import npc_brain

# =========================================================================
# 📱 MOBILE BUNDLE PATH COMPATIBILITY ROUTINE
# =========================================================================
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # When running bundled inside a mobile app store package
    BASE_DIR = sys._MEIPASS
else:
    # When running standard local executions from your desktop workspace
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📁 Establish structural file paths globally
DATABASE_PATH = os.path.join(BASE_DIR, "dnd_campaign.db")
# =========================================================================

def main(page: ft.Page):
    # Set up modern mobile layout dimensions inside a desktop split frame
    page.title = "M&M GM Voice & Lore Toolkit"
    page.window_width = 480
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK

    active_session_id = 1
    editing_npc_id = [None]  # Explicit mutable tracker list reference shell

    # 🌟 THE EXPLICIT SERVICES REGISTRATION:
    # Initialize the modern flet-audio control module
    audio_player = fta.Audio(
        src="",
        autoplay=False,
        volume=1.0,
    )

    # Append it straight to page services so the core engine keeps it alive
    page.services.append(audio_player)

    # --- GLOBAL UI TOAST NOTIFICATION BANNER ---
    def show_toast(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()

    # Base workspace layout visibility wrappers
    session_view_container = ft.Container(expand=True)
    forge_view_container = ft.Container(expand=True, visible=False)

    # --- SIDEBAR NAVIGATION RAIL CONTROLLER ---
    def handle_tab_change(e):
        if e.control.selected_index == 0:
            session_view_container.visible = True
            forge_view_container.visible = False
            refresh_chat_display()
            npc_selector.options = load_npc_options()
        else:
            session_view_container.visible = False
            forge_view_container.visible = True
            refresh_manage_list()
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        group_alignment=-1.0,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.PLAY_ARROW_ROUNDED, label="Live Session"),
            ft.NavigationRailDestination(icon=ft.Icons.BUILD_ROUNDED, label="NPC Forge"),
        ],
        on_change=handle_tab_change,
        bgcolor=ft.Colors.GREY_900
    )

    async def close_application(e):
        await page.window.close()

    close_app_button = ft.IconButton(
        icon=ft.Icons.POWER_SETTINGS_NEW_ROUNDED,
        icon_color=ft.Colors.RED_400,
        icon_size=28,
        tooltip="Close Toolkit Engine",
        on_click=close_application
    )

    # ==========================================
    # ENGINE BLOCK A: LIVE SESSION PANEL LOGIC
    # ==========================================
    def load_npc_options():
        #  New way (pointing directly to the mobile project copy)
        # 1. Dynamically find the folder this specific code file is currently running from
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Securely connect to the database sitting inside that exact folder path
        connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
        cursor = connection.cursor()
        cursor.execute("SELECT npc_id, name FROM npcs")
        rows = cursor.fetchall()
        connection.close()
        return [ft.dropdown.Option(key=str(row[0]), text=str(row[1])) for row in rows]

    def refresh_chat_display():
        chat_box.controls.clear()
        # 1. Dynamically find the folder this specific code file is currently running from
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Securely connect to the database sitting inside that exact folder path
        connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
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
                        bgcolor=ft.Colors.BLUE_GREY_800, padding=10, border_radius=10,
                        alignment=ft.Alignment(1, 0), margin=4
                    )
                )
            else:
                chat_box.controls.append(
                    ft.Container(
                        content=ft.Text(f"🎭 {npc_name}: {text}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.AMBER_900, padding=10, border_radius=10,
                        alignment=ft.Alignment(-1, 0), margin=4
                    )
                )
        page.update()

    def background_mic_task(npc_id):
        spoken_text = mic_listener.listen_to_player()
        status_text.value = "Idle - Waiting for activation"
        status_text.color = ft.Colors.GREY_500
        mic_button.disabled = False
        page.update()

        if not spoken_text:
            show_toast("Microphone timeout or silent input.", ft.Colors.RED)
            return

        refresh_chat_display()

        # 🌟 CLEAN & STABLE: main_app doesn't need to hunt for voice_id anymore!
        npc_brain.get_npc_response_with_memory(
            session_id=active_session_id,
            user_text=spoken_text,
            npc_name=npc_id,  # This is passing your database 'nid' or 'name' string
            audio_player_widget=audio_player
        )

        # Redraw the UI log screen view
        refresh_chat_display()

    def trigger_microphone(e):
        npc_id_str = npc_selector.value
        if not npc_id_str:
            show_toast("Error: Select an active NPC character first!", ft.Colors.RED)
            return

        npc_id = int(npc_id_str)
        status_text.value = ">>> 📢 SPEAK NOW! Talk to the NPC... <<<"
        status_text.color = ft.Colors.GREEN
        mic_button.disabled = True
        page.update()

        threading.Thread(target=background_mic_task, args=(npc_id,), daemon=True).start()

    def clear_history_clicked(e):
        """Safely wipes all past dialogue context logs completely offline without needing global variables."""
        try:
            # 1. Dynamically find the folder this specific main_app.py file is running from
            import os, sqlite3
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "dnd_campaign.db")

            # 2. Open direct database transaction lane
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            # 3. Purge dialogue text metrics tracking rows across tables
            cursor.execute("DELETE FROM dialogue")
            connection.commit()
            connection.close()

            # 4. REDRAW VISUAL SCREEN LAYOUT:
            # Explicitly clear out the visual chat boxes on the screen right here to force a blank slate!
            chat_box.controls.clear()
            page.update()

            show_toast("Campaign conversation logs wiped successfully!", ft.Colors.RED)
            print("[UI Sync] Dialogue data wiped successfully from local sandbox.")

        except Exception as err:
            print(f"[UI Error] Sweep execution failed: {err}")
            show_toast(f"Clear Error: {err}", ft.Colors.RED)

    # --- ASSEMBLE LIVE SESSION GRAPHIC COMPONENT PANELS ---
    session_header = ft.Container(content=ft.Column(
        [ft.Text("⚔️ Session Dashboard", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)]), padding=3)
    npc_selector = ft.Dropdown(label="Active Speaking NPC", border_color=ft.Colors.AMBER_400,
                               options=load_npc_options(), width=350)
    status_text = ft.Text("Idle - Waiting for activation", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500)
    chat_box = ft.Column(scroll=ft.ScrollMode.AUTO, height=320, width=350)

    # 1. DEFINE MIC BUTTON FIRST (Moved this up so Python registers it early!)
    mic_button = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.MIC, color=ft.Colors.BLACK),
                        ft.Text("Listen to Players", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)],
                       alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.Colors.AMBER_400, width=290, height=50, on_click=trigger_microphone
    )

    # 2. DEFINE COMBINED ROW SECOND (Now it can grab mic_button flawlessly)
    session_action_controls = ft.Row(
        [
            ft.Container(content=mic_button, width=290),
            ft.IconButton(
                icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                icon_color=ft.Colors.RED_400,
                icon_size=28,
                tooltip="Reset Memory Context",
                on_click=clear_history_clicked
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        width=350
    )

    # 3. MOUNT THE ROW CONTAINER LAST INTO THE PANEL WRAPPER
    session_view_container.content = ft.Container(
        width=350,
        content=ft.Column([
            session_header,
            ft.Container(content=npc_selector, padding=2),
            ft.Container(content=status_text, padding=2),
            ft.Container(
                content=chat_box, padding=4, border_radius=10, bgcolor=ft.Colors.BLACK,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_800), bottom=ft.BorderSide(1, ft.Colors.GREY_800),
                                 left=ft.BorderSide(1, ft.Colors.GREY_800), right=ft.BorderSide(1, ft.Colors.GREY_800))
            ),
            ft.Container(content=session_action_controls, padding=4)  # Using the action controls row here
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # ==========================================
    # ENGINE BLOCK B: NPC FORGE REGISTER LOGIC
    # ==========================================
    import manage_npcs
    def refresh_manage_list():
        roster_column.controls.clear()
        # 1. Dynamically find the folder this specific code file is currently running from
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Securely connect to the database sitting inside that exact folder path
        connection = sqlite3.connect(os.path.join(BASE_DIR, "dnd_campaign.db"))
        cursor = connection.cursor()
        cursor.execute("SELECT npc_id, name, voice_id, personality_prompt, faction, motivation, secrets FROM npcs")
        rows = cursor.fetchall()
        connection.close()

        for row in rows:
            nid, name, voice, prompt, fac, mot, sec = row

            def make_edit_handler(nid=nid, nm=name, vc=voice, pr=prompt, fc=fac, mt=mot, sc=sec):
                return lambda e: load_npc_for_editing(nid, nm, vc, pr, fc, mt, sc)

            def make_delete_handler(nid=nid, nm=name):
                return lambda e: remove_npc_clicked(nid, nm)

            roster_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, expand=True, size=13),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.AMBER_400, on_click=make_edit_handler(),
                                      icon_size=18),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400,
                                      on_click=make_delete_handler(), icon_size=18),
                    ]),
                    padding=2, border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_800))
                )
            )
        page.update()

    def load_npc_for_editing(npc_id, name, voice, prompt, fac, mot, sec):
        editing_npc_id[0] = npc_id
        name_input.value = name
        voice_dropdown.value = voice
        lore_input.value = ""
        faction_input.value = fac if fac else ""
        motivation_input.value = mot if mot else ""
        secrets_input.value = sec if sec else ""
        save_button_text.value = "Update Character Profile"
        show_toast(f"Loaded {name} into editing panels!", ft.Colors.AMBER_700)
        page.update()

    def remove_npc_clicked(npc_id, name):
        manage_npcs.delete_npc(npc_id)
        show_toast(f"Purged {name} from database.", ft.Colors.RED)
        refresh_manage_list()

    def save_npc_clicked(e):
        print("\n--- 🔍 DEBUG: FORGE BUTTON PRESSED ---")
        print(f"Raw Name Input: '{name_input.value}'")
        print(f"Raw Voice Dropdown Value: '{voice_dropdown.value}'")
        print(f"Raw Lore Input: '{lore_input.value}'")
        print(f"Current editing_npc_id state: {editing_npc_id}")
        print("---------------------------------------\n")

        # 1. Cleanly extract current screen form states
        name = name_input.value.strip() if name_input.value else ""
        voice = str(voice_dropdown.value) if voice_dropdown.value else "am_adam"
        lore = lore_input.value.strip() if lore_input.value else ""
        fac = faction_input.value.strip() if faction_input.value else "Independent"
        mot = motivation_input.value.strip() if motivation_input.value else "Standard behavior"
        sec = secrets_input.value.strip() if secrets_input.value else "No specific secrets known."

        if not name:
            show_toast("Error: Name field cannot be blank!", ft.Colors.RED)
            return
        if not lore:
            show_toast("Error: Behavior Prompt field cannot be blank!", ft.Colors.RED)
            return

        try:
            # 2. Dynamically calculate the local mobile database coordinate path right here
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "dnd_campaign.db")

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            # 3. Handle Updates vs New Entries directly within the local workspace transaction
            if editing_npc_id[0] is not None:
                # --- RUN UPDATE ROUTINE LOCALLY ---
                sql_command = """
                    UPDATE npcs 
                    SET name=?, voice_id=?, personality_prompt=?, faction=?, motivation=?, secrets=? 
                    WHERE npc_id=?;
                """
                cursor.execute(sql_command, (name, voice, lore, fac, mot, sec, editing_npc_id[0]))
                show_toast(f"Updated profile for {name}!", ft.Colors.GREEN)
                editing_npc_id[0] = None
                save_button_text.value = "Forge Character Profile"
            else:
                # --- RUN INSERT ROUTINE LOCALLY ---
                sql_command = """
                    INSERT INTO npcs (name, voice_id, personality_prompt, faction, motivation, secrets) 
                    VALUES (?, ?, ?, ?, ?, ?);
                """
                cursor.execute(sql_command, (name, voice, lore, fac, mot, sec))
                show_toast(f"Successfully saved {name}!", ft.Colors.GREEN)

            # Commit and cleanly close down the local transaction
            connection.commit()
            connection.close()

            # 4. REPAINT SCREEN LAYOUTS
            # Force your active panel selectors to sync up with the modified rows
            npc_selector.options = load_npc_options()
            npc_selector.update()

            # Wipe your input form boxes completely clean
            name_input.value = ""
            lore_input.value = ""
            faction_input.value = ""
            motivation_input.value = ""
            secrets_input.value = ""
            voice_dropdown.value = None

            # Redraw your management sidebar list column
            refresh_manage_list()
            print(f"[UI Sync Complete] Local transaction committed to mobile sandbox.")

        except Exception as err:
            print(f"[Database Error] Block failure: {err}")
            show_toast(f"Database Error: {err}", ft.Colors.RED)

    # --- ASSEMBLE NPC FORGE GRAPHIC COMPONENT PANELS ---
    forge_header = ft.Container(
        content=ft.Column([ft.Text("🎭 NPC Forge", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)]),
        padding=3)
    name_input = ft.TextField(label="NPC Name", border_color=ft.Colors.AMBER_400, width=350, text_size=13, height=42)
    voice_dropdown = ft.Dropdown(
        label="Select Fantasy Voice Archetype",
        border_color=ft.Colors.AMBER_400,
        width=350,
        height=42,
        options=[
            # --- 5 MALE ARCHETYPES ---
            ft.dropdown.Option("am_adam", "Dwarf/Goblin (Deep Gravelly Male)"),
            ft.dropdown.Option("am_michael", "Elf/Scholar (Ancient Wise Male)"),
            ft.dropdown.Option("am_echo", "Orc/Barbarian (Booming Chest Male)"),
            ft.dropdown.Option("pm_alex", "Rogue/Smuggler (Low Raspy Male)"),
            ft.dropdown.Option("bm_george", "Noble/King (Haughty British Male)"),

            # --- 5 FEMALE ARCHETYPES ---
            ft.dropdown.Option("af_nicole", "Goblin/Hag (Sharp Raspy Female)"),
            ft.dropdown.Option("af_bella", "Elf/Druid (Ethereal Melodic Female)"),
            ft.dropdown.Option("af_sky", "Orc/Commander (Stern Commanding Female)"),
            ft.dropdown.Option("af_sarah", "Rogue/Assassin (Deceptive Whisper Female)"),
            ft.dropdown.Option("bf_emma", "Noble/Queen (Crisp Precise Female)"),
        ],
    )

    lore_input = ft.TextField(label="Behavior Prompt", multiline=True, min_lines=1, max_lines=2,
                              border_color=ft.Colors.AMBER_400, width=350, text_size=13)
    faction_input = ft.TextField(label="Faction Affiliation", border_color=ft.Colors.AMBER_400, width=350, text_size=13,
                                 height=42)
    motivation_input = ft.TextField(label="Current Goal", border_color=ft.Colors.AMBER_400, width=350, text_size=13,
                                    height=42)
    secrets_input = ft.TextField(label="Hidden Lore Secrets", multiline=True, min_lines=1, max_lines=2,
                                 border_color=ft.Colors.AMBER_400, width=350, text_size=13)

    save_button_text = ft.Text("Forge Character Profile", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
    save_button = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.SAVE, color=ft.Colors.BLACK, size=18), save_button_text],
                       alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.Colors.AMBER_400, width=350, height=45, on_click=save_npc_clicked
    )
    roster_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=90, width=350)

    forge_view_container.content = ft.Container(
        width=350,
        content=ft.Column([
            forge_header,
            ft.Container(content=name_input, padding=1),
            ft.Container(content=voice_dropdown, padding=1),
            ft.Container(content=lore_input, padding=1),
            ft.Container(content=faction_input, padding=1),
            ft.Container(content=motivation_input, padding=1),
            ft.Container(content=secrets_input, padding=1),
            ft.Container(content=save_button, padding=3),
            ft.Text("⚙️ Manage NPC Campaign Roster", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500),
            ft.Container(
                content=roster_column, padding=4, border_radius=10, bgcolor=ft.Colors.BLACK,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_800), bottom=ft.BorderSide(1, ft.Colors.GREY_800),
                                 left=ft.BorderSide(1, ft.Colors.GREY_800), right=ft.BorderSide(1, ft.Colors.GREY_800))
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # ------------------------------------------
    # RENDER ENGINE MASTER MOUNT ASSEMBLIES
    # ------------------------------------------
    workspace_views = ft.Column([
        session_view_container,
        forge_view_container
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    sidebar_layout = ft.Column([
        ft.Container(content=nav_rail, expand=True),
        ft.Container(content=close_app_button, alignment=ft.Alignment(0, 0), padding=15)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=80)

    # UPDATE THIS BLOCK: Adding the invisible audio row to your layout stack
    page.add(
        ft.Row([
            ft.Container(content=workspace_views, expand=True, padding=5),
            ft.VerticalDivider(width=1, color=ft.Colors.GREY_800),
            sidebar_layout
        ], expand=True),


    )
    page.update()

    refresh_chat_display()


if __name__ == "__main__":
    import pyttsx3;

    print([v.name for v in pyttsx3.init().getProperty('voices')])

    ft.run(main)
