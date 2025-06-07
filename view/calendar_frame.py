# view/calendar_frame.py

from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar
from dateutil import parser
import webbrowser

from view.base_frame import BaseFrame
from helpers.google_calendar_helper import build_service


class CalendarFrame(BaseFrame):
    def __init__(self, master, controller):
        self.google_service = build_service()
        self.event_links = {}  # Store Treeview item ID -> event URL
        self._last_displayed = None  # For calendar month polling
        super().__init__(master, controller)

    def _go_back(self):
        from view.dashboard_frame import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def setup_ui(self):
        ttk.Button(self, text="← Back to Dashboard", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="Service Calendar", font=("Segoe UI", 16)).pack(pady=10)

        self.cal = Calendar(self, selectmode="day", date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)

        ttk.Button(self, text="🗓 View Events for Selected Day", command=self._load_selected_day).pack()
        ttk.Button(self, text="🗓 Show This Week's Events", command=self._load_week_events).pack(pady=10)

        self.events_list = ttk.Treeview(
            self,
            columns=("Start", "Summary", "Customer", "Vehicle"),
            show="headings",
            height=6
        )
        self.events_list.heading("Start", text="Start Time")
        self.events_list.heading("Summary", text="Event Summary")
        self.events_list.heading("Customer", text="Customer")
        self.events_list.heading("Vehicle", text="Vehicle")
        self.events_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.events_list.bind("<Double-1>", self._open_selected_event)
        self._poll_calendar_month()

    def refresh_data(self):
        self._load_week_events()
        self._highlight_calendar_days()

    def _load_week_events(self):
        now = datetime.utcnow().isoformat() + "Z"
        week_later = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        self.events_list.delete(*self.events_list.get_children())
        self.event_links.clear()

        try:
            events_result = self.google_service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=week_later,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            if not events:
                self.events_list.insert("", "end", values=("No events", "", "", ""))
                return

            for event in events:
                raw_start = event['start'].get('dateTime', event['start'].get('date'))
                start = self._format_event_time(raw_start)
                summary = event.get('summary', 'No Title').replace("[RTF]", "").strip()
                description = event.get("description", "")

                customer = vehicle = ""
                for line in description.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("customer & vehicle"):
                        vehicle_line = line.split(":", 1)[1].strip()
                        if " " in vehicle_line:
                            parts = vehicle_line.split(" ", 1)
                            customer, vehicle = parts[0].strip(), parts[1].strip()
                        else:
                            customer, vehicle = "Unknown", vehicle_line
                    elif line.lower().startswith("customer"):
                        customer = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("vehicle"):
                        vehicle = line.split(":", 1)[1].strip()

                item_id = self.events_list.insert("", "end", values=(start, summary, customer, vehicle))
                self.event_links[item_id] = event.get("htmlLink", "")

        except Exception as e:
            messagebox.showerror("Google Calendar Error", str(e))

    def _load_selected_day(self):
        selected_date = self.cal.get_date()
        start = f"{selected_date}T00:00:00-07:00"
        end = f"{selected_date}T23:59:59-07:00"

        self.events_list.delete(*self.events_list.get_children())
        self.event_links.clear()

        try:
            events_result = self.google_service.events().list(
                calendarId='primary',
                timeMin=start,
                timeMax=end,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            if not events:
                self.events_list.insert("", "end", values=("No events", "", "", ""))
                return

            for event in events:
                raw_start = event['start'].get('dateTime', event['start'].get('date'))
                start = self._format_event_time(raw_start)
                summary = event.get('summary', 'No Title').replace("[RTF]", "").strip()

                description = event.get("description", "")
                customer = vehicle = ""

                for line in description.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("customer & vehicle"):
                        vehicle_line = line.split(":", 1)[1].strip()
                        if " " in vehicle_line:
                            parts = vehicle_line.split(" ", 1)
                            customer, vehicle = parts[0].strip(), parts[1].strip()
                        else:
                            customer, vehicle = "Unknown", vehicle_line

                item_id = self.events_list.insert("", "end", values=(start, summary, customer, vehicle))
                self.event_links[item_id] = event.get("htmlLink", "")

        except Exception as e:
            messagebox.showerror("Calendar Error", str(e))

    def _highlight_calendar_days(self):
        try:
            month, year = self.cal.get_displayed_month()
            first_date = datetime(year, month, 1)
            last_date = (first_date + timedelta(days=40)).replace(day=1) - timedelta(days=1)

            time_min = first_date.isoformat() + "Z"
            time_max = last_date.isoformat() + "Z"

            events_result = self.google_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            self.cal.calevent_remove('all')
            events = events_result.get('items', [])

            for event in events:
                raw = event['start'].get('dateTime', event['start'].get('date'))
                dt = parser.parse(raw)
                summary = event.get("summary", "Event").replace("[RTF]", "").strip()
                description = event.get("description", "")
                label = f"{summary}\n{description}"
                self.cal.calevent_create(dt.date(), label, "service")

            self.cal.tag_config("service", background="lightblue", foreground="black")

        except Exception as e:
            messagebox.showerror("Calendar Highlight Error", str(e))

    def _poll_calendar_month(self):
        try:
            current = self.cal.get_displayed_month()
            if current != self._last_displayed:
                self._last_displayed = current
                self._highlight_calendar_days()
        except Exception as e:
            print("Polling error:", e)
        self.after(500, self._poll_calendar_month)

    def _open_selected_event(self, event):
        selected = self.events_list.focus()
        if selected and selected in self.event_links:
            url = self.event_links[selected]
            if url:
                webbrowser.open(url)

    def _format_event_time(self, dt_string):
        try:
            dt = parser.parse(dt_string)
            return dt.strftime("%B %d, %Y – %I:%M %p")
        except Exception:
            return dt_string
