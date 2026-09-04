import sqlite3
import flet as ft
import manage_npcs


def main(page: ft.Page):
    page.title = "D&D NPC Voice Toolkit"
    page.window_width = 450
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    # Editing state tracker
    editing_npc_id = [None]

    def show_toast(message, color_name=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(content=ft.Text(message, color=ft.Colors.WHITE), bgcolor=color_name, duration=3000)
        page.snack_bar.open = True
        page.update()

    # Refreshes the management list layout
    def refresh_manage_list():
        roster_column.controls.clear()
        connection = sqlite3.connect("dnd_campaign.db")
        cursor = connection.cursor()
        cursor.execute("SELECT npc_id, name, voice_id, personality_prompt, faction, motivation, secrets FROM npcs")
        rows = cursor.fetchall()
        connection.close()

        for npc_id, name, voice, prompt, fac, mot, sec in rows:
            # Inline function generators for buttons to lock variable scopes properly
            def make_edit_handler(nid=npc_id, nm=name, vc=voice, pr=prompt, fc=fac, mt=mot, sc=sec):
                return lambda e: load_npc_for_editing(nid, nm, vc, pr, fc, mt, sc)

            def make_delete_handler(nid=npc_id, nm=name):
                return lambda e: remove_npc_clicked(nid, nm)

            roster_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, expand=True),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.AMBER_400, on_click=make_edit_handler()),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400,
                                      on_click=make_delete_handler()),
                    ]),
                    padding=5,
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_800))
                )
            )
        page.update()

    def load_npc_for_editing(npc_id, name, voice, prompt, fac, mot, sec):
        editing_npc_id[0] = npc_id
        name_input.value = name
        voice_dropdown.value = voice
        lore_input.value = prompt
        faction_input.value = fac if fac else ""
        motivation_input.value = mot if mot else ""
        secrets_input.value = sec if sec else ""
        save_button.content.controls[1].value = "Update Character Profile"
        show_toast(f"Loaded {name} into editing boxes above!", ft.Colors.AMBER_700)
        page.update()

    def remove_npc_clicked(npc_id, name):
        manage_npcs.delete_npc(npc_id)
        show_toast(f"Purged {name} from the database.", ft.Colors.RED)
        refresh_manage_list()

    def save_npc_clicked(e):
        name = name_input.value.strip()
        voice = voice_dropdown.value
        lore = lore_input.value.strip()
        fac = faction_input.value.strip()
        mot = motivation_input.value.strip()
        sec = secrets_input.value.strip()

        if not name or not voice or not lore:
            show_toast("Error: Name, Voice, and Personality prompt are required!", ft.Colors.RED)
            return

        try:
            if editing_npc_id[0] is not None:
                # Update loop configuration path
                manage_npcs.update_npc(editing_npc_id[0], name, voice, lore, fac, mot, sec)
                show_toast(f"Updated profile for {name} successfully!", ft.Colors.GREEN)
                editing_npc_id[0] = None
                save_button.content.controls[1].value = "Forge Character Profile"
            else:
                # Standard fresh data entry append loop
                manage_npcs.add_new_npc(name, voice, lore, fac, mot, sec)
                show_toast(f"Successfully saved {name} to campaign registry!", ft.Colors.GREEN)

            # Form resetting sequence fields
            name_input.value = ""
            lore_input.value = ""
            faction_input.value = ""
            motivation_input.value = ""
            secrets_input.value = ""
            voice_dropdown.value = None
            refresh_manage_list()

        except Exception as err:
            show_toast(f"Database Handler Error: {err}", ft.Colors.RED)

    # --- UI DESIGN BLUEPRINTS (NARROWED WIDTH TO 350PX) ---

    header = ft.Container(
        content=ft.Column([
            ft.Text("🎭 NPC Forge", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
        ]), padding=5
    )

    name_input = ft.TextField(label="NPC Character Name", border_color=ft.Colors.AMBER_400, width=350)

    voice_dropdown = ft.Dropdown(
        label="Select Voice Identity", border_color=ft.Colors.AMBER_400, width=350,
        options=[
            ft.dropdown.Option("onyx", "Onyx (Deep, Gravelly Male)"),
            ft.dropdown.Option("echo", "Echo (Balanced, Crisp Male)"),
            ft.dropdown.Option("fable", "Fable (Dramatic, Raspy Neutral)"),
            ft.dropdown.Option("alloy", "Alloy (Neutral, Direct Voice)"),
            ft.dropdown.Option("shimmer", "Shimmer (Professional, Clear Female)"),
            ft.dropdown.Option("nova", "Nova (Energetic, Bright Female)"),
        ],
    )

    lore_input = ft.TextField(label="Personality Prompt (Base Behavior)", multiline=True, min_lines=2, max_lines=4,
                              border_color=ft.Colors.AMBER_400, width=350)

    # NEW THREE SPECIALIZED CONTEXT TEXTBOXES
    faction_input = ft.TextField(label="Faction / Group Affiliation", border_color=ft.Colors.AMBER_400, width=350,
                                 hint_text="e.g., Zhentarim, Local City Guard, Thieves Guild")
    motivation_input = ft.TextField(label="Current Goal / Motivation", border_color=ft.Colors.AMBER_400, width=350,
                                    hint_text="e.g., Wants to secure a bribe, looking for his lost ring")
    secrets_input = ft.TextField(label="Known Campaign Secrets / Lore", multiline=True, min_lines=2, max_lines=3,
                                 border_color=ft.Colors.AMBER_400, width=350,
                                 hint_text="e.g., Knows that Captain Rolf accepts smuggler coin at the docks")

    save_button = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.SAVE, color=ft.Colors.BLACK),
                        ft.Text("Forge Character Profile", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)],
                       alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.Colors.AMBER_400, width=350, height=50, on_click=save_npc_clicked
    )

    roster_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=150, width=350)

    # --- MOUNT LAYOUT ITEMS TO APP CANVAS WINDOW ---
    page.add(
        ft.Container(
            content=ft.Column([
                header,
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(content=name_input, padding=3),
                ft.Container(content=voice_dropdown, padding=3),
                ft.Container(content=lore_input, padding=3),
                ft.Container(content=faction_input, padding=3),
                ft.Container(content=motivation_input, padding=3),
                ft.Container(content=secrets_input, padding=3),
                ft.Container(content=save_button, padding=10),
                ft.Text("⚙️ Manage Loaded NPC Campaign Roster", size=12, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_500),
                ft.Container(content=roster_column, padding=5,
                             border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_800),
                                              bottom=ft.BorderSide(1, ft.Colors.GREY_800),
                                              left=ft.BorderSide(1, ft.Colors.GREY_800),
                                              right=ft.BorderSide(1, ft.Colors.GREY_800)), border_radius=10,
                             bgcolor=ft.Colors.BLACK)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=5
        )
    )
    refresh_manage_list()


if __name__ == "__main__":
    ft.run(main)

