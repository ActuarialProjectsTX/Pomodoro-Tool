import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont, simpledialog
import json
import os
import winsound

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro & Meditation App")
        self.root.geometry("700x500")

        # Variables
        self.tasks = {}  # {task_name: pomodoro_count}
        self.selected_task = tk.StringVar()
        self.pomodoro_duration = tk.StringVar(value="25")
        self.break_duration = tk.StringVar(value="5")
        self.meditation_duration = tk.StringVar(value="10")
        self.schedule_str = tk.StringVar(value="P2,B1")
        self.timer_id = None
        self.seconds_left = 0
        self.session_type = "IDLE"  # "IDLE", "POMODORO", "BREAK", "MEDITATION"
        self.session_sequence = []
        self.current_session_index = 0
        self.theme = "Light"
        self.font_family = "Arial"
        self.font_size = 12
        self.pomodoro_sound_enabled = tk.IntVar(value=1)
        self.meditation_sound_enabled = tk.IntVar(value=1)
        self.meditation_guide_text = """Mindfulness Meditation Guide:
This practice helps you stay present by focusing on your breath.
Steps:
1. Find a quiet, comfortable place to sit.
2. Close your eyes and take a few deep breaths.
3. Notice the air flowing into your nose and out of your mouth.
4. If thoughts arise, gently let them go and return to your breathing."""

        # Load saved data
        self.load_data()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tab frames
        self.pomodoro_frame = ttk.Frame(self.notebook)
        self.meditation_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pomodoro_frame, text="Pomodoro")
        self.notebook.add(self.meditation_frame, text="Meditation")
        self.notebook.add(self.settings_frame, text="Settings")

        # Build UI for each tab
        self.build_pomodoro_ui()
        self.build_meditation_ui()
        self.build_settings_ui()

        # Apply initial theme
        self.apply_theme()

    ### UI Construction Methods

    def build_pomodoro_ui(self):
        # Task selection
        ttk.Label(self.pomodoro_frame, text="Select Task:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.task_combobox = ttk.Combobox(self.pomodoro_frame, textvariable=self.selected_task)
        self.task_combobox.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.pomodoro_frame, text="Add Task", command=self.add_task).grid(row=0, column=2, padx=5, pady=5)

        # Pomodoro duration
        ttk.Label(self.pomodoro_frame, text="Pomodoro Duration (min):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.pomodoro_frame, textvariable=self.pomodoro_duration, width=10).grid(row=1, column=1, padx=5, pady=5)

        # Break duration
        ttk.Label(self.pomodoro_frame, text="Break Duration (min):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.pomodoro_frame, textvariable=self.break_duration, width=10).grid(row=2, column=1, padx=5, pady=5)

        # Schedule input
        ttk.Label(self.pomodoro_frame, text="Schedule (e.g., P2,B1):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.pomodoro_frame, textvariable=self.schedule_str, width=15).grid(row=3, column=1, padx=5, pady=5)

        # Control buttons
        self.start_button = ttk.Button(self.pomodoro_frame, text="Start Session", command=self.start_session)
        self.start_button.grid(row=4, column=0, padx=5, pady=10)
        self.stop_button = ttk.Button(self.pomodoro_frame, text="Stop Session", command=self.stop_session, state="disabled")
        self.stop_button.grid(row=4, column=1, padx=5, pady=10)

        # Timer display
        self.timer_label = ttk.Label(self.pomodoro_frame, text="00:00", font=("Arial", 24))
        self.timer_label.grid(row=5, column=0, columnspan=3, pady=10)

        # Task list
        self.task_tree = ttk.Treeview(self.pomodoro_frame, columns=("Task", "Pomodoros"), show="headings", height=8)
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Pomodoros", text="Pomodoros")
        self.task_tree.column("Task", width=300)
        self.task_tree.column("Pomodoros", width=100)
        self.task_tree.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        # Guide button
        ttk.Button(self.pomodoro_frame, text="Pomodoro Guide", command=self.show_pomodoro_guide).grid(row=7, column=0, columnspan=3, pady=5)

        # Sound option
        ttk.Checkbutton(self.pomodoro_frame, text="Play sound when session ends", variable=self.pomodoro_sound_enabled).grid(row=8, column=0, columnspan=3, pady=5)

        # Populate task list
        for task, count in self.tasks.items():
            self.task_tree.insert("", "end", values=(task, count))
            self.task_combobox["values"] = list(self.tasks.keys())

    def build_meditation_ui(self):
        # Duration input
        ttk.Label(self.meditation_frame, text="Meditation Duration (min):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.meditation_frame, textvariable=self.meditation_duration, width=10).grid(row=0, column=1, padx=5, pady=5)

        # Control buttons
        self.meditation_start_button = ttk.Button(self.meditation_frame, text="Start Meditation", command=self.start_meditation)
        self.meditation_start_button.grid(row=1, column=0, padx=5, pady=10)
        self.meditation_stop_button = ttk.Button(self.meditation_frame, text="Stop Meditation", command=self.stop_meditation, state="disabled")
        self.meditation_stop_button.grid(row=1, column=1, padx=5, pady=10)

        # Timer display
        self.meditation_timer_label = ttk.Label(self.meditation_frame, text="00:00", font=("Arial", 24))
        self.meditation_timer_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Guide button
        ttk.Button(self.meditation_frame, text="Meditation Guide", command=self.show_meditation_guide).grid(row=3, column=0, columnspan=2, pady=5)

        # Sound option
        ttk.Checkbutton(self.meditation_frame, text="Play sound when timer ends", variable=self.meditation_sound_enabled).grid(row=4, column=0, columnspan=2, pady=5)

    def build_settings_ui(self):
        # Theme selection
        ttk.Label(self.settings_frame, text="Theme:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.theme_combobox = ttk.Combobox(self.settings_frame, values=["Light", "Dark"], state="readonly")
        self.theme_combobox.set(self.theme)
        self.theme_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.update_theme)

        # Font family selection
        ttk.Label(self.settings_frame, text="Font Family:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.font_family_combobox = ttk.Combobox(self.settings_frame, values=list(tkfont.families()), state="readonly")
        self.font_family_combobox.set(self.font_family)
        self.font_family_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.font_family_combobox.bind("<<ComboboxSelected>>", self.update_font)

        # Font size selection
        ttk.Label(self.settings_frame, text="Font Size:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.font_size_combobox = ttk.Combobox(self.settings_frame, values=list(range(8, 21)), state="readonly")
        self.font_size_combobox.set(self.font_size)
        self.font_size_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.font_size_combobox.bind("<<ComboboxSelected>>", self.update_font)

    ### Data Management

    def load_data(self):
        # Load tasks
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                self.tasks = json.load(f)
        # Load settings
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.theme = settings.get("theme", "Light")
                self.font_family = settings.get("font_family", "Arial")
                self.font_size = settings.get("font_size", 12)
                self.pomodoro_sound_enabled.set(settings.get("pomodoro_sound", 1))
                self.meditation_sound_enabled.set(settings.get("meditation_sound", 1))
        # Load meditation guide
        if os.path.exists("meditation_guide.txt"):
            with open("meditation_guide.txt", "r") as f:
                self.meditation_guide_text = f.read()

    def save_data(self):
        # Save tasks
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)
        # Save settings
        settings = {
            "theme": self.theme,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "pomodoro_sound": self.pomodoro_sound_enabled.get(),
            "meditation_sound": self.meditation_sound_enabled.get()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        # Save meditation guide
        with open("meditation_guide.txt", "w") as f:
            f.write(self.meditation_guide_text)

    ### Theme and Customization

    def apply_theme(self):
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        if self.theme == "Light":
            bg = "#f0f0f0"
            fg = "black"
            tab_bg = "#e0e0e0"
            button_bg = "#4CAF50"
            button_fg = "white"
        else:  # Dark
            bg = "#333333"
            fg = "white"
            tab_bg = "#555555"
            button_bg = "#4CAF50"
            button_fg = "white"

        # Configure styles
        style.configure("TLabel", background=bg, foreground=fg, font=(self.font_family, self.font_size))
        style.configure("TButton", background=button_bg, foreground=button_fg, font=(self.font_family, self.font_size))
        style.map("TButton", background=[("active", "#45a049")])
        style.configure("TEntry", fieldbackground=bg, foreground=fg, font=(self.font_family, self.font_size))
        style.configure("TCombobox", fieldbackground=bg, foreground=fg, font=(self.font_family, self.font_size))
        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", background=tab_bg, foreground=fg, font=(self.font_family, self.font_size))
        style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, font=(self.font_family, self.font_size))
        style.map("Treeview", background=[("selected", "blue")], foreground=[("selected", "white")])

        # Timer labels with larger font
        timer_font = (self.font_family, 24)
        self.timer_label.config(font=timer_font)
        self.meditation_timer_label.config(font=timer_font)

        # Root background
        self.root.config(bg=bg)

    def update_theme(self, event):
        self.theme = self.theme_combobox.get()
        self.apply_theme()
        self.save_data()

    def update_font(self, event):
        self.font_family = self.font_family_combobox.get()
        self.font_size = int(self.font_size_combobox.get())
        self.apply_theme()
        self.save_data()

    ### Pomodoro Functionality

    def add_task(self):
        task_name = simpledialog.askstring("Add Task", "Enter task name:")
        if task_name and task_name not in self.tasks:
            self.tasks[task_name] = 0
            self.task_tree.insert("", "end", values=(task_name, 0))
            self.task_combobox["values"] = list(self.tasks.keys())
            if not self.selected_task.get():
                self.selected_task.set(task_name)
            self.save_data()

    def parse_schedule(self):
        try:
            parts = self.schedule_str.get().split(",")
            sequence = []
            for part in parts:
                type_ = part[0].upper()
                count = int(part[1:])
                if type_ not in ["P", "B", "M"]:
                    raise ValueError
                sequence.extend([type_] * count)
            return sequence
        except (ValueError, IndexError):
            messagebox.showwarning("Invalid Schedule", "Using default: P2,B1")
            return ["P", "P", "B"]

    def start_session(self):
        if self.session_type != "IDLE":
            return
        if not self.selected_task.get():
            messagebox.showwarning("Warning", "Please select a task.")
            return
        self.session_sequence = self.parse_schedule()
        self.current_session_index = 0
        self.start_current_session()

    def start_current_session(self):
        if self.current_session_index >= len(self.session_sequence):
            self.stop_session()
            return
        session_type = self.session_sequence[self.current_session_index]
        try:
            if session_type == "P":
                minutes = int(self.pomodoro_duration.get())
                label_text = "Pomodoro"
            elif session_type == "B":
                minutes = int(self.break_duration.get())
                label_text = "Break"
            elif session_type == "M":
                minutes = int(self.meditation_duration.get())
                label_text = "Meditation"
            else:
                raise ValueError
            self.session_type = session_type
            self.seconds_left = minutes * 60
            self.timer_label.config(text=f"{label_text}: {self.format_time(self.seconds_left)}")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.update_timer()
        except ValueError:
            messagebox.showerror("Error", "Invalid duration. Please enter a positive number.")

    def update_timer(self):
        if self.seconds_left > 0:
            self.timer_label.config(text=f"{self.session_type}: {self.format_time(self.seconds_left)}")
            self.seconds_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.finish_session()

    def finish_session(self):
        if self.session_type == "P":
            task_name = self.selected_task.get()
            if task_name in self.tasks:
                self.tasks[task_name] += 1
                for item in self.task_tree.get_children():
                    if self.task_tree.item(item)["values"][0] == task_name:
                        self.task_tree.item(item, values=(task_name, self.tasks[task_name]))
                        break
                self.save_data()
        if self.pomodoro_sound_enabled.get():
            winsound.Beep(1000, 1000)
        self.current_session_index += 1
        self.start_current_session()

    def stop_session(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.session_type = "IDLE"
        self.timer_label.config(text="00:00")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    ### Meditation Functionality

    def start_meditation(self):
        if self.session_type != "IDLE":
            messagebox.showwarning("Warning", "A session is already running.")
            return
        try:
            minutes = int(self.meditation_duration.get())
            if minutes <= 0:
                raise ValueError
            self.session_type = "M"
            self.seconds_left = minutes * 60
            self.meditation_timer_label.config(text=self.format_time(self.seconds_left))
            self.meditation_start_button.config(state="disabled")
            self.meditation_stop_button.config(state="normal")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.update_meditation_timer()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive number for meditation duration.")

    def update_meditation_timer(self):
        if self.seconds_left > 0:
            self.meditation_timer_label.config(text=self.format_time(self.seconds_left))
            self.seconds_left -= 1
            self.timer_id = self.root.after(1000, self.update_meditation_timer)
        else:
            messagebox.showinfo("Meditation Done", "Meditation session completed!")
            if self.meditation_sound_enabled.get():
                winsound.Beep(1000, 1000)
            self.meditation_timer_label.config(text="00:00")
            self.meditation_start_button.config(state="normal")
            self.meditation_stop_button.config(state="disabled")
            self.session_type = "IDLE"

    def stop_meditation(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.meditation_timer_label.config(text="00:00")
        self.meditation_start_button.config(state="normal")
        self.meditation_stop_button.config(state="disabled")
        self.session_type = "IDLE"

    ### Guides

    def show_pomodoro_guide(self):
        guide = """Pomodoro Technique Guide:
1. Choose a task.
2. Set a schedule (e.g., P2,B1 for 2 Pomodoros and 1 Break).
3. Work during Pomodoros, rest during breaks, and meditate as scheduled.
4. Repeat or adjust as needed."""
        messagebox.showinfo("Pomodoro Guide", guide)

    def show_meditation_guide(self):
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Meditation Guide")
        guide_window.geometry("400x300")
        text_area = tk.Text(guide_window, wrap="word", font=(self.font_family, self.font_size))
        text_area.insert("1.0", self.meditation_guide_text)
        text_area.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(guide_window, text="Save", command=lambda: self.save_meditation_guide(text_area.get("1.0", "end-1c"), guide_window)).pack(pady=5)

    def save_meditation_guide(self, new_text, window):
        self.meditation_guide_text = new_text
        self.save_data()
        window.destroy()

    ### Helper Methods

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()