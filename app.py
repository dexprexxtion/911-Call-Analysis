"""A simple Tkinter dashboard for exploring fictional 911 call data."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd


DATA_FILE = Path(__file__).parent / "data" / "911_calls.csv"
REQUIRED_COLUMNS = {"Date", "Location", "Call_Type", "Call_Time"}


def load_call_data():
    """Load the CSV into a pandas DataFrame and tidy its text columns."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Could not find the data file: {DATA_FILE}")

    calls = pd.read_csv(DATA_FILE)
    missing_columns = REQUIRED_COLUMNS.difference(calls.columns)
    if missing_columns:
        raise ValueError(
            "The CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    calls["Date"] = pd.to_datetime(calls["Date"])
    for column in ("Location", "Call_Type", "Call_Time"):
        calls[column] = calls[column].astype("string").str.strip()

    calls["Date"] = calls["Date"].dt.strftime("%Y-%m-%d")
    return calls


class CallAnalysisApp:
    """Create the responsive dashboard and its basic navigation controls."""

    def __init__(self, root, calls):
        self.root = root
        self.calls = calls
        self.is_fullscreen = False

        root.title("911 Call Analysis")
        root.geometry("1050x700")
        root.minsize(700, 480)

        # Configure weighted rows and columns so the dashboard grows with its window.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        self._build_header()
        self._build_location_controls()
        self._build_placeholders()
        self._build_status()

        # F11 toggles fullscreen, while Escape returns to the normal window.
        root.bind("<F11>", self.toggle_fullscreen)
        root.bind("<Escape>", self.exit_fullscreen)

    def _build_header(self):
        """Show the project title and a button for changing window display mode."""
        header = ttk.Frame(self.root, padding=(24, 20))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header, text="911 Call Analysis", font=("Segoe UI", 22, "bold")
        ).grid(row=0, column=0, sticky="w")
        self.fullscreen_button = ttk.Button(
            header, text="Enter Full Screen", command=self.toggle_fullscreen
        )
        self.fullscreen_button.grid(row=0, column=1, sticky="e")

    def _build_location_controls(self):
        """Populate a location dropdown using the unique locations in the CSV."""
        controls = ttk.Frame(self.root, padding=(24, 8))
        controls.grid(row=1, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Choose a location:").grid(
            row=0, column=0, padx=(0, 12), sticky="w"
        )
        self.location = tk.StringVar()
        self.location_box = ttk.Combobox(
            controls,
            textvariable=self.location,
            values=sorted(self.calls["Location"].dropna().unique().tolist()),
            state="readonly",
        )
        self.location_box.grid(row=0, column=1, sticky="ew")
        self.location_box.bind("<<ComboboxSelected>>", self.update_selection)
        if self.location_box["values"]:
            self.location_box.current(0)

    def _build_placeholders(self):
        """Reserve responsive dashboard panels for charts and summaries added later."""
        content = ttk.Frame(self.root, padding=(24, 16, 24, 16))
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1, uniform="panels")
        content.columnconfigure(1, weight=1, uniform="panels")
        content.rowconfigure(1, weight=1)

        self.selection_label = ttk.Label(
            content,
            text=f"Selected location: {self.location.get()}",
            font=("Segoe UI", 13, "bold"),
        )
        self.selection_label.grid(
            row=0, column=0, columnspan=2, sticky="nw", pady=(0, 14)
        )

        self._add_placeholder(
            content,
            column=0,
            title="Calls by type",
            message="A chart showing call categories will appear here.",
        )
        self._add_placeholder(
            content,
            column=1,
            title="Calls by time",
            message="A chart showing call times will appear here.",
        )

    @staticmethod
    def _add_placeholder(parent, column, title, message):
        """Draw a labeled panel to mark where a future chart will be displayed."""
        panel = ttk.LabelFrame(parent, text=title, padding=20)
        panel.grid(
            row=1, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0)
        )
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        ttk.Label(panel, text=message, anchor="center", justify="center").grid(
            row=0, column=0, sticky="nsew"
        )

    def _build_status(self):
        """Display a short note describing the sample data currently loaded."""
        status = ttk.Label(
            self.root,
            text=f"Loaded {len(self.calls)} fictional sample calls from the CSV file.",
            padding=(24, 12),
            anchor="w",
        )
        status.grid(row=3, column=0, sticky="ew")

    def update_selection(self, _event=None):
        """Update the dashboard label when another location is selected."""
        self.selection_label.configure(
            text=f"Selected location: {self.location.get()}"
        )

    def toggle_fullscreen(self, _event=None):
        """Switch between fullscreen and a regular resizable window."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        button_text = "Exit Full Screen" if self.is_fullscreen else "Enter Full Screen"
        self.fullscreen_button.configure(text=button_text)

    def exit_fullscreen(self, _event=None):
        """Return to the normal window when Escape is pressed."""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.fullscreen_button.configure(text="Enter Full Screen")


def main():
    """Load the sample data, report expected file errors, and start the GUI."""
    root = tk.Tk()
    try:
        calls = load_call_data()
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        messagebox.showerror("Unable to load call data", str(error), parent=root)
        root.destroy()
        return

    CallAnalysisApp(root, calls)
    root.mainloop()


if __name__ == "__main__":
    main()
