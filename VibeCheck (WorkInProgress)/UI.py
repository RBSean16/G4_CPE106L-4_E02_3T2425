import flet as ft
import datetime
import requests
import webbrowser
import json
from typing import Optional

BG_COLOR = "#f8f9fa"
PRIMARY_COLOR = "#0d6efd"
WHITE = "#ffffff"
TEXT_MUTED = "#000000"
BORDER_COLOR = "#e9ecef"
SUCCESS_COLOR = "#198754"
INFO_COLOR = "#000000"
SECONDARY_COLOR = "#6c757d"
SHADOW_COLOR = "#1A000000"

user_id = 1  # Hardcoded for now, but could be dynamic later
API_BASE_URL = "http://127.0.0.1:8000/api"  # FastAPI base URL

def main(page: ft.Page):
    page.title = "Community Mental Health Tracker"
    page.bgcolor = BG_COLOR
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    mood_items_ref = []
    journal_entry_ref = ft.Ref[ft.TextField]()
    recommendation_output_ref = ft.Ref[ft.Container]()
    recommendation_text_ref = ft.Ref[ft.Text]()

    def save_file_result(e: ft.FilePickerResultEvent):
        if e.path:
            try:
                journal_text = journal_entry_ref.current.value
                if journal_text:
                    with open(e.path, "w", encoding="utf-8") as f:
                        f.write(journal_text)
                    show_snack_bar("Journal exported successfully!", SUCCESS_COLOR)
                else:
                    show_snack_bar("Journal is empty. Nothing to export.", "red500")
            except Exception as ex:
                show_snack_bar(f"Failed to save file: {ex}", "red500")

    file_picker = ft.FilePicker(on_result=save_file_result)
    page.overlay.append(file_picker)

    def show_snack_bar(message: str, color: str):
        """Helper function to show snack bar messages"""
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def check_api_connection() -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{API_BASE_URL.replace('/api', '')}/docs", timeout=2)
            return response.status_code == 200
        except:
            return False

    def handle_login(e):
        username = username_field.value
        password = password_field.value  # Add this line to get the password from the password field
        if not username:
            username_field.error_text = "Username cannot be empty"
            page.update()
            return

        # Check API connection first
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        try:
            # Create or check user
            response = requests.post(f"{API_BASE_URL}/create-user", json={
                "user_id": user_id,
                "name": username,
                "password": password  # Add this line to include the password in the request
            }, timeout=5)

            if response.status_code == 200:
                show_snack_bar("Login successful!", SUCCESS_COLOR)
                page.go("/main")
            else:
                show_snack_bar("Login failed. Please try again.", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    def select_mood(e):
        # Check API connection first
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        clicked_container = e.control
        score_map = {
            "Happy": 9,
            "Content": 7,
            "Neutral": 5,
            "Sad": 3,
            "Angry": 1
        }
        label = clicked_container.content.controls[1].value
        score = score_map.get(label, 5)

        try:
            response = requests.post(f"{API_BASE_URL}/mood-entry", json={
                "user_id": user_id,
                "mood_score": score,
                "notes": f"Selected mood: {label}"
            }, timeout=5)

            if response.status_code == 200:
                show_snack_bar(f"Mood '{label}' saved!", SUCCESS_COLOR)
                # Update visual selection
                for item_container in mood_items_ref:
                    is_selected = (item_container == clicked_container)
                    item_container.bgcolor = PRIMARY_COLOR if is_selected else WHITE
                    item_container.border = ft.border.all(1, PRIMARY_COLOR if is_selected else BORDER_COLOR)
                    item_container.content.controls[0].color = WHITE if is_selected else None
                    item_container.content.controls[1].color = WHITE if is_selected else TEXT_MUTED
                page.update()
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else 'Server error'
                show_snack_bar(f"Error: {error_msg}", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    def save_entry(e):
        content = journal_entry_ref.current.value
        if not content:
            show_snack_bar("Journal entry is empty.", "red500")
            return

        # Check API connection first
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/journal-entry",
                json={"user_id": user_id, "content": content},
                timeout=5
            )
            if response.status_code == 200:
                journal_entry_ref.current.value = ""  # Clear the input field
                show_snack_bar("Journal entry saved successfully!", SUCCESS_COLOR)
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else 'Server error'
                show_snack_bar(f"Error: {error_msg}", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    def get_recommendations(e):
        try:
            response = requests.get(f"{API_BASE_URL}/recommendation/{user_id}")
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            rec = response.json()
            recommendation_text_ref.current.value = f"{rec['strategy']} — {rec['reason']}"
            recommendation_output_ref.current.visible = True
        except requests.exceptions.RequestException as e:
            page.snack_bar = ft.SnackBar(content=ft.Text("Failed to fetch recommendation."), bgcolor="red500")
            page.snack_bar.open = True
        except KeyError as e:
            page.snack_bar = ft.SnackBar(content=ft.Text("Invalid response from API."), bgcolor="red500")
            page.snack_bar.open = True
        page.update()

    def export_to_txt(e):
        journal_text = journal_entry_ref.current.value
        if not journal_text:
            page.snack_bar = ft.SnackBar(content=ft.Text("Journal is empty. Nothing to export."), bgcolor="red500")
            page.snack_bar.open = True
            page.update()
            return

        # Use the file picker to save
        file_picker.save_file(
            dialog_title="Save Journal Entry",
            file_name=f"journal_entry_{datetime.date.today().isoformat()}.txt",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["txt"]
        )

    def view_mood_chart(e):
        """Open mood trend chart in browser"""
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        try:
            # Make request to generate chart
            response = requests.get(f"{API_BASE_URL}/mood-trend/{user_id}", timeout=10)
            if response.status_code == 200:
                # Open the chart in browser
                chart_url = f"http://127.0.0.1:8000/static/mood_trend_{user_id}.png"
                webbrowser.open(chart_url)
                show_snack_bar("Mood chart opened in browser!", SUCCESS_COLOR)
            else:
                error_msg = response.json().get('detail', 'No mood data found') if response.headers.get('content-type') == 'application/json' else 'Server error'
                show_snack_bar(f"Error: {error_msg}", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    def view_journal_heatmap(e):
        """Open journal heatmap in browser"""
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        try:
            # Make request to generate heatmap
            response = requests.get(f"{API_BASE_URL}/journal-heatmap/{user_id}", timeout=10)
            if response.status_code == 200:
                # Open the heatmap in browser
                heatmap_url = f"http://127.0.0.1:8000/static/journal_heatmap_{user_id}.png"
                webbrowser.open(heatmap_url)
                show_snack_bar("Journal heatmap opened in browser!", SUCCESS_COLOR)
            else:
                error_msg = response.json().get('detail', 'No journal data found') if response.headers.get('content-type') == 'application/json' else 'Server error'
                show_snack_bar(f"Error: {error_msg}", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    def view_wellness_scores(e):
        """Open wellness scores chart in browser"""
        if not check_api_connection():
            show_snack_bar("API server is not running. Please start the FastAPI server first.", "red500")
            return

        try:
            # Make request to generate wellness scores chart
            response = requests.get(f"{API_BASE_URL}/wellness-scores", timeout=10)
            if response.status_code == 200:
                # Open the chart in browser
                chart_url = f"http://127.0.0.1:8000/static/wellness_scores.png"
                webbrowser.open(chart_url)
                show_snack_bar("Wellness scores chart opened in browser!", SUCCESS_COLOR)
            else:
                show_snack_bar("Error generating wellness scores chart", "red500")
        except requests.exceptions.RequestException as ex:
            show_snack_bar(f"Connection error: {ex}", "red500")

    username_field = ft.TextField(label="Username", autofocus=True, width=300, height=40, border_radius=10, bgcolor=WHITE, border=ft.border.all(1, BORDER_COLOR), focused_color=ft.border.all(1, PRIMARY_COLOR), color="black")
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300, height=40, border_radius=10, bgcolor=WHITE, border=ft.border.all(1, BORDER_COLOR), focused_color=ft.border.all(1, PRIMARY_COLOR), color="black")

    def create_login_view():
        return ft.View(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BOLD, color="#000000"),
                        ft.Text("Sign in to continue to the tracker.", color=TEXT_MUTED),
                        username_field,
                        password_field,
                        ft.ElevatedButton("Login", on_click=handle_login, width=400, bgcolor=PRIMARY_COLOR, color=WHITE),
                        ft.Text("Forgot Password?", color=TEXT_MUTED, size=12),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=400, padding=40, border_radius=10, bgcolor=WHITE,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=SHADOW_COLOR)
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def create_main_view():
        nonlocal mood_items_ref
        mood_items_ref = []
        moods = [("😄", "Happy"), ("😊", "Content"), ("😐", "Neutral"), ("😟", "Sad"), ("😠", "Angry")]
        for icon, label in moods:
            is_selected = (label == "Neutral")
            container = ft.Container(
                content=ft.Column([
                    ft.Text(icon, size=24, color=WHITE if is_selected else None),
                    ft.Text(label, size=12, color=WHITE if is_selected else TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                on_click=select_mood, padding=10, border_radius=8,
                bgcolor=PRIMARY_COLOR if is_selected else WHITE,
                border=ft.border.all(1, PRIMARY_COLOR if is_selected else BORDER_COLOR),
                tooltip=f"Select {label}"
            )
            mood_items_ref.append(container)

        today = datetime.date.today()
        calendar_grid = ft.GridView(expand=False, runs_count=7, max_extent=40, child_aspect_ratio=1.0, spacing=5, run_spacing=5)
        for day in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            calendar_grid.controls.append(ft.Container(ft.Text(day, weight=ft.FontWeight.BOLD, color=TEXT_MUTED), alignment=ft.alignment.center))

        first_day_of_month = today.replace(day=1)
        weekday_of_first = (first_day_of_month.weekday() + 1) % 7
        for _ in range(weekday_of_first): calendar_grid.controls.append(ft.Container())

        days_in_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        for day_num in range(1, days_in_month + 1):
            is_today = (day_num == today.day)
            has_entry = False
            day_container = ft.Container(
                content=ft.Text(str(day_num), color=WHITE if is_today else None),
                alignment=ft.alignment.center, border_radius=20,
                bgcolor=PRIMARY_COLOR if is_today else ("green100" if has_entry else None)
            )
            calendar_grid.controls.append(day_container)

        left_sidebar = ft.Container(
            content=ft.Column([
                ft.Text("Mood Tracker", weight=ft.FontWeight.BOLD, size=18, color="#000000"),
                ft.Text(f"How are you feeling today? ({today})", color=TEXT_MUTED, size=12),
                ft.Row(controls=mood_items_ref, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text("Journaling Streak", weight=ft.FontWeight.BOLD, size=18, color="#000000"),
                calendar_grid,
                ft.Column([
                    ft.Divider(),
                    ft.Text("Local Support:", color=TEXT_MUTED, size=12),
                    ft.Text("Community Center Hotline", color=PRIMARY_COLOR, selectable=True),
                    ft.Text("Find a Local Therapist", color=PRIMARY_COLOR, selectable=True)
                ], expand=True, alignment=ft.MainAxisAlignment.END, spacing=5)
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=350, bgcolor=WHITE, border_radius=10, padding=20,
            shadow=ft.BoxShadow(blur_radius=4, color=SHADOW_COLOR)
        )

        journal_entry_ref.current = ft.TextField(
            ref=journal_entry_ref, multiline=True, min_lines=10,
            hint_text="Write about your day, your thoughts, and your feelings...",
            border=ft.InputBorder.OUTLINE, border_radius=8, expand=True, color="black"
        )
        main_content = ft.Container(
            content=ft.Column([
                ft.Text(f"Journal Entry for {today}", weight=ft.FontWeight.BOLD, size=18, color="#000000"),
                journal_entry_ref.current,
                ft.ElevatedButton("Save Entry", on_click=save_entry, bgcolor=PRIMARY_COLOR, color=WHITE, height=50)
            ], spacing=15),
            expand=True, bgcolor=WHITE, border_radius=10, padding=20,
            shadow=ft.BoxShadow(blur_radius=4, color=SHADOW_COLOR)
        )

        recommendation_text_ref.current = ft.Text("", size=14)
        recommendation_output_ref.current = ft.Container(
            ref=recommendation_output_ref, visible=False,
            content=ft.Column([
                ft.Text("Recommendations:", weight=ft.FontWeight.BOLD),
                recommendation_text_ref.current
            ]),
            padding=15, border_radius=8, border=ft.border.all(1, "blue200"), bgcolor="blue50"
        )

        right_sidebar = ft.Container(
            content=ft.Column([
                ft.Text("AI-Powered Insights", weight=ft.FontWeight.BOLD, size=18, color="#000000"),
                ft.Text("Let our AI assistant provide feedback based on your journal.", color=TEXT_MUTED, size=12),
                ft.ElevatedButton("Analyze with AI", on_click=get_recommendations, bgcolor=INFO_COLOR, color=WHITE, height=50),
                recommendation_output_ref.current,
                ft.Divider(height=20),
                ft.Text("Data Export", weight=ft.FontWeight.BOLD, size=18, color="#000000"),
                ft.Text("Export your data for personal use or to share with a professional.", color=TEXT_MUTED, size=12),
                ft.ElevatedButton("Export Journal to .txt", on_click=export_to_txt, bgcolor=SECONDARY_COLOR, color=WHITE, height=50),
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=350, bgcolor=WHITE, border_radius=10, padding=20,
            shadow=ft.BoxShadow(blur_radius=4, color=SHADOW_COLOR)
        )

        return ft.View(
            route="/main",
            controls=[ft.Row([left_sidebar, main_content, right_sidebar], spacing=15, expand=True)],
            padding=15
        )

    def route_change(route):
        page.views.clear()
        if page.route == "/main":
            page.views.append(create_main_view())
        else:
            page.views.append(create_login_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)