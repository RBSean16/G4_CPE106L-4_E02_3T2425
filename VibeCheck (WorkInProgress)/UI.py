# UI.py

import flet as ft
import datetime
import requests
from typing import Optional

# --- UI Constants ---
BG_COLOR = "#f8f9fa"
PRIMARY_COLOR = "#0d6efd"
WHITE = "#ffffff"
TEXT_COLOR = "#212529"
BLACK = "#000000"
TEXT_MUTED = "#6c757d"
BORDER_COLOR = "#dee2e6"
SUCCESS_COLOR = "#198754"
ERROR_COLOR = "#dc3545" 
SHADOW_COLOR = "#6c757d"

# --- API & App State ---
API_BASE_URL = "http://127.0.0.1:8000/api"
app_state = {"user_id": None, "user_name": None}

def main(page: ft.Page):
    page.title = "VibeCheck"
    page.bgcolor = BG_COLOR
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UI Element Refs ---
    journal_entry_ref = ft.Ref[ft.TextField]()
    calendar_grid_ref = ft.Ref[ft.GridView]()

    # --- MAIN UI VIEW CREATORS ---

    def create_login_view():
        login_username_field = ft.TextField(label="Username", autofocus=True, color=BLACK)
        login_password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, color=BLACK)
        error_text = ft.Text(value="", color=ERROR_COLOR, visible=False)

        def handle_login(e):
            error_text.visible = False
            page.update()
            if not login_username_field.value or not login_password_field.value:
                error_text.value = "Please enter a username and password."
                error_text.visible = True
                page.update()
                return
            try:
                response = requests.post(f"{API_BASE_URL}/login", json={"name": login_username_field.value, "password": login_password_field.value})
                if response.status_code == 200:
                    data = response.json()
                    app_state["user_id"] = data["user_id"]
                    app_state["user_name"] = data["name"]
                    page.go("/main")
                else:
                    error_text.value = response.json().get("detail", "An unknown error occurred.")
                    error_text.visible = True
                    page.update()
            except requests.exceptions.RequestException:
                error_text.value = "Cannot connect to the server."
                error_text.visible = True
                page.update()
        
        login_password_field.on_submit = handle_login

        return ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("VibeCheck", size=32, weight=ft.FontWeight.BOLD, color=BLACK),
                        ft.Text("A Journal for Your Mind, A Map for Your Mood", color=TEXT_MUTED),
                        login_username_field,
                        login_password_field,
                        error_text,
                        ft.ElevatedButton("Login", width=400, on_click=handle_login, bgcolor=PRIMARY_COLOR, color=WHITE),
                        ft.Column(
                            [
                                ft.Text("No account yet?"),
                                ft.TextButton("Create one here.", on_click=lambda _: page.go("/register"), style=ft.ButtonStyle(padding=0)),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=400, padding=40, border_radius=10, bgcolor=WHITE,
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, SHADOW_COLOR)),
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def create_registration_view():
        reg_username_field = ft.TextField(label="Username", autofocus=True, color=BLACK)
        reg_password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, color=BLACK)
        error_text = ft.Text(value="", color=ERROR_COLOR, visible=False)

        def handle_registration(e):
            error_text.visible = False
            page.update()
            if not reg_username_field.value or not reg_password_field.value:
                error_text.value = "Username and password cannot be empty."
                error_text.visible = True
                page.update()
                return
            try:
                response = requests.post(f"{API_BASE_URL}/register", json={"name": reg_username_field.value, "password": reg_password_field.value})
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account created! Please log in."), bgcolor=SUCCESS_COLOR)
                    page.snack_bar.open = True
                    page.go("/")
                else:
                    error_text.value = response.json().get("detail", "Registration failed.")
                    error_text.visible = True
                    page.update()
            except requests.exceptions.RequestException:
                error_text.value = "Cannot connect to the server."
                error_text.visible = True
                page.update()
        
        reg_password_field.on_submit = handle_registration

        return ft.View(
            "/register",
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Create Your Account", size=24, weight=ft.FontWeight.BOLD, color=BLACK),
                        reg_username_field,
                        reg_password_field,
                        error_text,
                        ft.ElevatedButton("Create Account", width=400, on_click=handle_registration, bgcolor=SUCCESS_COLOR, color=WHITE),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=400, padding=40, border_radius=10, bgcolor=WHITE,
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, SHADOW_COLOR)),
                )
            ],
            appbar=ft.AppBar(title=ft.Text("Register"), leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def create_main_view():
        # --- Helper function for showing SnackBars on the main page ---
        def show_snack_bar(message: str, color: str):
            page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
            page.snack_bar.open = True
            page.update()

        def select_mood(e):
            if not app_state["user_id"]: return
            score_map = {"Happy": 9, "Content": 7, "Neutral": 5, "Sad": 3, "Angry": 1}
            label = e.control.data
            score = score_map.get(label, 5)
            try:
                requests.post(f"{API_BASE_URL}/mood-entry", json={"user_id": app_state["user_id"], "mood_score": score, "notes": f"Selected mood: {label}"})
                show_snack_bar(f"Mood '{label}' saved!", SUCCESS_COLOR)
                for item_container in e.control.parent.controls:
                    is_selected = (item_container == e.control)
                    item_container.bgcolor = PRIMARY_COLOR if is_selected else WHITE
                    item_container.border = ft.border.all(2, PRIMARY_COLOR if is_selected else BORDER_COLOR)
                    item_container.content.controls[0].color = WHITE if is_selected else TEXT_COLOR
                    item_container.content.controls[1].color = WHITE if is_selected else TEXT_MUTED
                page.update()
            except requests.exceptions.RequestException: show_snack_bar("Connection error.", ERROR_COLOR)

        def save_entry(e):
            if not app_state["user_id"]: return
            content = journal_entry_ref.current.value
            if not content:
                show_snack_bar("Journal entry is empty.", ERROR_COLOR)
                return
            try:
                requests.post(f"{API_BASE_URL}/journal-entry", json={"user_id": app_state["user_id"], "content": content})
                journal_entry_ref.current.value = ""
                show_snack_bar("Journal entry saved!", SUCCESS_COLOR)
                update_calendar_with_entries()
                page.update()
            except requests.exceptions.RequestException: show_snack_bar("Connection error.", ERROR_COLOR)
        
        def update_calendar_with_entries():
            if not app_state["user_id"] or not calendar_grid_ref.current: return
            try:
                response = requests.get(f"{API_BASE_URL}/journal-dates/{app_state['user_id']}")
                if response.status_code == 200:
                    entry_dates = set(response.json().get("dates", []))
                    today_str = datetime.date.today().isoformat()
                    for control in calendar_grid_ref.current.controls[7:]:
                        if isinstance(control, ft.Container) and control.data:
                            day_str = control.data
                            if day_str == today_str:
                                control.bgcolor = PRIMARY_COLOR
                                control.content.color = WHITE
                            elif day_str in entry_dates:
                                control.bgcolor = ft.Colors.with_opacity(0.3, SUCCESS_COLOR)
                                control.content.color = BLACK
                            else:
                                control.bgcolor = None
                                control.content.color = TEXT_COLOR
                    page.update()
            except requests.exceptions.RequestException: pass

        mood_items = []
        moods = [("😄", "Happy"), ("😊", "Content"), ("😐", "Neutral"), ("😟", "Sad"), ("😠", "Angry")]
        for icon, label in moods:
            mood_items.append(
                ft.Container(
                    content=ft.Column([ft.Text(icon, size=30), ft.Text(label, size=12, color=TEXT_MUTED)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    on_click=select_mood, data=label, padding=10, border_radius=8, border=ft.border.all(1, BORDER_COLOR), tooltip=f"Select {label}"
                )
            )

        today = datetime.date.today()
        calendar_grid_ref.current = ft.GridView(ref=calendar_grid_ref, expand=False, runs_count=7, max_extent=40, child_aspect_ratio=1.0, spacing=5, run_spacing=5)
        for day in ["M", "T", "W", "T", "F", "S", "S"]:
            calendar_grid_ref.current.controls.append(ft.Container(ft.Text(day, weight=ft.FontWeight.BOLD, color=TEXT_MUTED), alignment=ft.alignment.center))
        
        first_day_of_month = today.replace(day=1)
        for _ in range(first_day_of_month.weekday()): calendar_grid_ref.current.controls.append(ft.Container())
        
        days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        for day_num in range(1, days_in_month + 1):
            day_date = datetime.date(today.year, today.month, day_num)
            calendar_grid_ref.current.controls.append(
                ft.Container(content=ft.Text(str(day_num), color=TEXT_COLOR), alignment=ft.alignment.center, border_radius=20, data=day_date.isoformat())
            )

        left_sidebar = ft.Container(
            content=ft.Column([
                ft.Text("How are you feeling?", weight=ft.FontWeight.BOLD, size=20, color=BLACK),
                ft.Row(controls=mood_items, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Divider(),
                ft.Text("Journaling Activity", weight=ft.FontWeight.BOLD, size=18, color=BLACK),
                calendar_grid_ref.current,
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=400, padding=20, bgcolor=WHITE, border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, SHADOW_COLOR))
        )
        main_content = ft.Container(
            content=ft.Column([
                ft.Text(f"Journal Entry for {today.strftime('%B %d, %Y')}", weight=ft.FontWeight.BOLD, size=18, color=BLACK),
                ft.TextField(ref=journal_entry_ref, multiline=True, min_lines=10, expand=True, border_color=BORDER_COLOR, color=BLACK),
                ft.ElevatedButton("Save Entry", on_click=save_entry, icon=ft.Icons.SAVE, bgcolor=PRIMARY_COLOR, color=WHITE),
            ], spacing=15, expand=True),
            expand=True, padding=20, bgcolor=WHITE, border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, SHADOW_COLOR))
        )
        right_sidebar = ft.Container(
            content=ft.Column([
                ft.Text("Insights & Visuals", weight=ft.FontWeight.BOLD, size=18, color=BLACK),
                ft.Divider(),
                ft.Text("Local Support Resources", weight=ft.FontWeight.BOLD, size=16, color=BLACK),
                ft.Text("National Center for Mental Health Crisis Hotline", size=12),
                ft.Text("1553", size=14, weight=ft.FontWeight.BOLD, selectable=True),
                ft.TextButton("Mapúa University Health Services", url="https://www.mapua.edu.ph/pages/offices/health-services"),
            ], spacing=8),
            width=300, padding=20, bgcolor=WHITE, border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, SHADOW_COLOR))
        )
        update_calendar_with_entries()
        return ft.View(
            "/main",
            [ft.Row([left_sidebar, main_content, right_sidebar], spacing=20, expand=True)],
            appbar=ft.AppBar(
                title=ft.Text(f"VibeCheck - {app_state.get('user_name', '')}"),
                actions=[ft.IconButton(icon=ft.Icons.LOGOUT, tooltip="Logout", on_click=lambda _: page.go("/"))],
            ),
        )

    # --- Route Management ---
    def route_change(e):
        page.views.clear()
        if page.route == "/main":
            page.views.append(create_main_view())
        elif page.route == "/register":
            page.views.append(create_registration_view())
        else:
            app_state["user_id"] = None
            app_state["user_name"] = None
            page.views.append(create_login_view())
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)