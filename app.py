"""Work Tracker — Desktop app for daily work logging & weekly reports."""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import (
    init_db, get_categories, add_task, get_tasks_for_date,
    get_tasks_for_week, get_all_tasks, delete_task, get_today_summary,
    get_week_stats, add_category, delete_category,
)
from report import generate_weekly_report

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAVY = "#1E2761"
ICE = "#CADCFC"
WHITE = "#FFFFFF"
DARK_BG = "#1a1a2e"
CARD_BG = "#16213e"
TEXT_COLOR = "#e0e0e0"
MUTED = "#8899BB"
ACCENT = "#028090"
DANGER = "#B85042"


class WorkTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Work Tracker")
        self.geometry("1100x700")
        self.minsize(900, 600)

        init_db()
        self.categories = get_categories()

        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=DARK_BG)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.header = ctk.CTkFrame(self.main_frame, fg_color=NAVY, height=60, corner_radius=8)
        self.header.pack(fill="x", pady=(0, 10))
        self.header.pack_propagate(False)

        ctk.CTkLabel(
            self.header, text="Work Tracker",
            font=ctk.CTkFont(family="Georgia", size=24, weight="bold"),
            text_color=WHITE,
        ).pack(side="left", padx=20, pady=15)

        # Tab buttons
        self.tab_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.tab_frame.pack(side="right", padx=20)

        self.tabs = {}
        for tab_name in ["Dashboard", "This Week", "History", "Settings"]:
            btn = ctk.CTkButton(
                self.tab_frame, text=tab_name,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=ICE,
                hover_color="#2a3a6e",
                height=40,
                command=lambda t=tab_name: self.switch_tab(t),
            )
            btn.pack(side="left", padx=5)
            self.tabs[tab_name] = btn

        # Content area
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=DARK_BG)
        self.content_frame.pack(fill="both", expand=True)

        # Report button at bottom
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        self.bottom_frame.pack(fill="x", pady=(10, 0))
        self.bottom_frame.pack_propagate(False)

        self.report_btn = ctk.CTkButton(
            self.bottom_frame, text="Generate Weekly Report",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color="#026a78",
            text_color=WHITE,
            height=40, width=200,
            command=self.generate_report,
        )
        self.report_btn.pack(side="right", padx=20)

        # Start with Dashboard
        self.current_tab = None
        self.switch_tab("Dashboard")
        
        # Force window to appear
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.focus_force()

    def switch_tab(self, tab_name):
        # Update button colors
        for name, btn in self.tabs.items():
            if name == tab_name:
                btn.configure(fg_color="#2a3a6e", text_color=WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=ICE)

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.current_tab = tab_name

        if tab_name == "Dashboard":
            self.render_dashboard()
        elif tab_name == "This Week":
            self.render_week()
        elif tab_name == "History":
            self.render_history()
        elif tab_name == "Settings":
            self.render_settings()

    def render_dashboard(self):
        today = datetime.now().strftime("%Y-%m-%d")
        today_label = datetime.now().strftime("%A, %B %d, %Y")

        # Title
        ctk.CTkLabel(
            self.content_frame, text="Dashboard",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=WHITE, anchor="w",
        ).pack(fill="x", pady=(10, 5), padx=20)

        ctk.CTkLabel(
            self.content_frame, text=today_label,
            font=ctk.CTkFont(size=13), text_color=MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 15), padx=20)

        # Quick-add form
        form = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=10)
        form.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            form, text="Log a Task",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ICE, anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 8))

        # Category + Duration row
        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row1, text="Category:", font=ctk.CTkFont(size=13), text_color=TEXT_COLOR).pack(side="left", padx=(0, 8))
        self.cat_var = ctk.StringVar(value=self.categories[0]["name"] if self.categories else "")
        ctk.CTkOptionMenu(
            row1, variable=self.cat_var,
            values=[c["name"] for c in self.categories],
            width=180, height=32,
            fg_color=NAVY, button_color=NAVY, button_hover_color="#2a3a6e",
        ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row1, text="Min:", font=ctk.CTkFont(size=13), text_color=TEXT_COLOR).pack(side="left", padx=(0, 8))
        self.duration_var = ctk.StringVar(value="0")
        ctk.CTkEntry(row1, textvariable=self.duration_var, width=60, height=32).pack(side="left")

        # Description row
        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row2, text="Task:", font=ctk.CTkFont(size=13), text_color=TEXT_COLOR).pack(side="left", padx=(0, 8))
        self.desc_var = ctk.StringVar()
        desc_entry = ctk.CTkEntry(
            row2, textvariable=self.desc_var, height=32,
            placeholder_text="What did you work on?",
        )
        desc_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        desc_entry.bind("<Return>", lambda e: self.add_task())

        # Add button
        ctk.CTkButton(
            form, text="Add",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT, hover_color="#026a78",
            height=36, width=100,
            command=self.add_task,
        ).pack(padx=15, pady=12)

        # Today's tasks
        summary = get_today_summary()
        ctk.CTkLabel(
            self.content_frame,
            text=f"Today — {summary['count']} task(s), {summary['total_minutes']} min",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ICE, anchor="w",
        ).pack(fill="x", pady=(10, 8), padx=20)

        # Task list
        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20)

        if not summary["tasks"]:
            ctk.CTkLabel(
                scroll, text="No tasks logged yet.",
                font=ctk.CTkFont(size=14), text_color=MUTED,
            ).pack(pady=30)
        else:
            for task in summary["tasks"]:
                self.render_task_row(scroll, task)

    def render_task_row(self, parent, task):
        row = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=6)
        row.pack(fill="x", pady=2)

        cat_color = "#1E2761"
        for c in self.categories:
            if c["name"] == task["category"]:
                cat_color = c["color"]
                break

        ctk.CTkLabel(
            row, text=task["category"],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=WHITE, fg_color=cat_color,
            corner_radius=4, width=130,
        ).pack(side="left", padx=8, pady=6)

        ctk.CTkLabel(
            row, text=task["description"],
            font=ctk.CTkFont(size=13), text_color=TEXT_COLOR,
            anchor="w",
        ).pack(side="left", padx=8, pady=6, fill="x", expand=True)

        dur = f"{task['duration_minutes']}min" if task["duration_minutes"] > 0 else "—"
        ctk.CTkLabel(
            row, text=dur,
            font=ctk.CTkFont(size=12), text_color=MUTED, width=50,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            row, text="", width=28, height=28,
            fg_color=DANGER, hover_color="#9a3a2e",
            font=ctk.CTkFont(size=11),
            command=lambda tid=task["id"]: self.delete_task(tid),
        ).pack(side="left", padx=8, pady=4)

    def add_task(self):
        desc = self.desc_var.get().strip()
        if not desc:
            messagebox.showwarning("Missing", "Please enter a task description.")
            return

        cat = self.cat_var.get()
        try:
            duration = int(self.duration_var.get() or 0)
        except ValueError:
            duration = 0

        today = datetime.now().strftime("%Y-%m-%d")
        add_task(today, cat, desc, duration)

        self.desc_var.set("")
        self.duration_var.set("0")
        self.switch_tab("Dashboard")

    def delete_task(self, task_id):
        if messagebox.askyesno("Delete", "Delete this task?"):
            delete_task(task_id)
            self.switch_tab(self.current_tab)

    def render_week(self):
        ctk.CTkLabel(
            self.content_frame, text="This Week",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=WHITE, anchor="w",
        ).pack(fill="x", pady=(10, 5), padx=20)

        monday = datetime.now() - timedelta(days=datetime.now().weekday())
        sunday = monday + timedelta(days=6)
        week_label = f"{monday.strftime('%b %d')} — {sunday.strftime('%b %d, %Y')}"

        ctk.CTkLabel(
            self.content_frame, text=week_label,
            font=ctk.CTkFont(size=13), text_color=MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 15), padx=20)

        stats = get_week_stats()
        total_tasks = sum(s["count"] for s in stats.values())
        total_mins = sum(s["total_minutes"] for s in stats.values())

        # Stats bar
        stats_bar = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=10)
        stats_bar.pack(fill="x", padx=20, pady=(0, 15))

        for label, value in [("Tasks", str(total_tasks)), ("Time", f"{total_mins}min"), ("Categories", str(len(stats)))]:
            cell = ctk.CTkFrame(stats_bar, fg_color="transparent")
            cell.pack(side="left", padx=40, pady=12)
            ctk.CTkLabel(cell, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=ICE).pack()
            ctk.CTkLabel(cell, text=label, font=ctk.CTkFont(size=11), text_color=MUTED).pack()

        # Tasks by category
        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20)

        if not stats:
            ctk.CTkLabel(
                scroll, text="No tasks this week.",
                font=ctk.CTkFont(size=15), text_color=MUTED,
            ).pack(pady=40)
        else:
            for cat_name, cat_stats in stats.items():
                cat_color = "#1E2761"
                for c in self.categories:
                    if c["name"] == cat_name:
                        cat_color = c["color"]
                        break

                header = ctk.CTkFrame(scroll, fg_color="transparent")
                header.pack(fill="x", pady=(12, 4))

                ctk.CTkLabel(
                    header, text=cat_name,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=cat_color, anchor="w",
                ).pack(side="left")

                ctk.CTkLabel(
                    header, text=f"{cat_stats['count']} tasks · {cat_stats['total_minutes']}min",
                    font=ctk.CTkFont(size=12), text_color=MUTED,
                ).pack(side="right")

                for task in cat_stats["tasks"]:
                    self.render_task_row(scroll, task)

    def render_history(self):
        ctk.CTkLabel(
            self.content_frame, text="History",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=WHITE, anchor="w",
        ).pack(fill="x", pady=(10, 15), padx=20)

        all_tasks = get_all_tasks()

        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20)

        if not all_tasks:
            ctk.CTkLabel(
                scroll, text="No tasks logged yet.",
                font=ctk.CTkFont(size=15), text_color=MUTED,
            ).pack(pady=40)
            return

        from collections import defaultdict
        by_date = defaultdict(list)
        for t in all_tasks:
            by_date[t["date"]].append(t)

        for date_str in sorted(by_date.keys(), reverse=True):
            date_label = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d, %Y")
            day_tasks = by_date[date_str]
            total_min = sum(t["duration_minutes"] for t in day_tasks)

            header = ctk.CTkFrame(scroll, fg_color="transparent")
            header.pack(fill="x", pady=(12, 4))

            ctk.CTkLabel(
                header, text=date_label,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=ICE, anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                header, text=f"{len(day_tasks)} tasks · {total_min}min",
                font=ctk.CTkFont(size=12), text_color=MUTED,
            ).pack(side="right")

            for task in day_tasks:
                self.render_task_row(scroll, task)

    def render_settings(self):
        ctk.CTkLabel(
            self.content_frame, text="Settings",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=WHITE, anchor="w",
        ).pack(fill="x", pady=(10, 15), padx=20)

        # Categories
        ctk.CTkLabel(
            self.content_frame, text="Categories",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ICE, anchor="w",
        ).pack(fill="x", pady=(0, 8), padx=20)

        cat_frame = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=10)
        cat_frame.pack(fill="x", padx=20, pady=(0, 15))

        for cat in self.categories:
            row = ctk.CTkFrame(cat_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            dot = ctk.CTkFrame(row, width=14, height=14, fg_color=cat["color"], corner_radius=7)
            dot.pack(side="left", padx=(8, 10))
            dot.pack_propagate(False)

            ctk.CTkLabel(
                row, text=cat["name"],
                font=ctk.CTkFont(size=14), text_color=TEXT_COLOR, anchor="w",
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color=DANGER, hover_color="#9a3a2e",
                font=ctk.CTkFont(size=11),
                command=lambda n=cat["name"]: self.delete_category(n),
            ).pack(side="right", padx=5)

        # Add category
        add_frame = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=10)
        add_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            add_frame, text="Add Category",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ICE, anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 8))

        row = ctk.CTkFrame(add_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=8)

        self.new_cat_var = ctk.StringVar()
        ctk.CTkEntry(
            row, textvariable=self.new_cat_var, width=220, height=32,
            placeholder_text="Category name",
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row, text="Add", height=32, width=70,
            fg_color=ACCENT, hover_color="#026a78",
            command=self.add_category,
        ).pack(side="left")

        # Data
        ctk.CTkLabel(
            self.content_frame, text="Data",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ICE, anchor="w",
        ).pack(fill="x", pady=(15, 8), padx=20)

        data_frame = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=10)
        data_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            data_frame, text="Export Database",
            height=38, fg_color=NAVY, hover_color="#2a3a6e",
            command=self.export_db,
        ).pack(padx=12, pady=10, fill="x")

        ctk.CTkButton(
            data_frame, text="Clear All Data",
            height=38, fg_color=DANGER, hover_color="#9a3a2e",
            command=self.clear_all,
        ).pack(padx=12, pady=(0, 10), fill="x")

    def add_category(self):
        name = self.new_cat_var.get().strip()
        if not name:
            return
        try:
            add_category(name)
            self.categories = get_categories()
            self.new_cat_var.set("")
            self.switch_tab("Settings")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_category(self, name):
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            delete_category(name)
            self.categories = get_categories()
            self.switch_tab("Settings")

    def export_db(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfile="work_tracker_export.db",
        )
        if path:
            import shutil
            shutil.copy2(os.path.join(os.path.dirname(__file__), "work_tracker.db"), path)
            messagebox.showinfo("Exported", f"Database exported to:\n{path}")

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Delete ALL tasks?"):
            from db import get_conn
            conn = get_conn()
            conn.execute("DELETE FROM tasks")
            conn.commit()
            conn.close()
            self.switch_tab(self.current_tab)

    def generate_report(self):
        self.report_btn.configure(text="Generating...", state="disabled")
        self.update()

        def _do():
            try:
                path = generate_weekly_report()
                self.after(0, lambda: self.report_done(path))
            except Exception as e:
                self.after(0, lambda: self.report_error(str(e)))

        threading.Thread(target=_do, daemon=True).start()

    def report_done(self, path):
        self.report_btn.configure(text="Generate Weekly Report", state="normal")
        messagebox.showinfo("Report Generated", f"Saved to:\n\n{path}")

    def report_error(self, error):
        self.report_btn.configure(text="Generate Weekly Report", state="normal")
        messagebox.showerror("Error", f"Failed to generate report:\n\n{error}")


if __name__ == "__main__":
    try:
        print("Launching Work Tracker...", flush=True)
        app = WorkTrackerApp()
        print("App initialized. Forcing window to show...", flush=True)
        
        # Force window to appear
        app.update_idletasks()
        app.deiconify()
        app.lift()
        app.focus_force()
        app.attributes('-topmost', True)
        app.after(1000, lambda: app.attributes('-topmost', False))
        
        print("Window should be visible now. Starting mainloop...", flush=True)
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
