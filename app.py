"""A simple Tkinter app for exploring fictional 911 call data."""

# Import Tkinter for the window and pandas for reading and grouping the data.
from pathlib import Path
import random
import tkinter as tk
from tkinter import ttk

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Read the incident CSV into a pandas DataFrame.
data_file = Path(__file__).parent / "data" / "911_calls.csv"
calls = pd.read_csv(data_file)

# List the locations shown in the sidebar.
locations = [
    "North Loop",
    "Chelsea",
    "Station",
    "Central",
    "Downtown",
    "Bel Air",
    "Brookhaven",
]

# Create the main window and let the chart area expand when resized.
window = tk.Tk()
window.title("911 Call Analysis")
window.geometry("1100x700")
window.minsize(900, 550)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

# Make labels, buttons, and the incident table easier to read.
style = ttk.Style(window)
style.configure(".", font=("Segoe UI", 12))
style.configure("TButton", padding=8)
style.configure("Treeview", rowheight=30)
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 15,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    }
)

# Put the project title on the left and the author names on the right.
header = ttk.Frame(window, padding=(20, 15))
header.grid(row=0, column=0, sticky="ew")
header.columnconfigure(0, weight=1)
ttk.Label(header, text="911 Call Analysis", font=("Segoe UI", 26, "bold")).grid(
    row=0, column=0, sticky="w"
)
ttk.Label(
    header,
    text="by Ketan Chowdhury and Sagnik Biswas",
    font=("Segoe UI", 13),
).grid(row=0, column=1, sticky="e")

# Divide the window into a location sidebar and a chart area.
main_area = ttk.Frame(window, padding=(20, 5, 20, 15))
main_area.grid(row=1, column=0, sticky="nsew")
main_area.columnconfigure(1, weight=1)
main_area.rowconfigure(0, weight=1)

# Show the location list and the Analyze button in the left sidebar.
sidebar = ttk.Frame(main_area, padding=(0, 0, 18, 0))
sidebar.grid(row=0, column=0, sticky="ns")
ttk.Label(sidebar, text="Choose a location:", font=("Segoe UI", 12, "bold")).grid(
    row=0, column=0, sticky="w", pady=(0, 8)
)
location_list = tk.Listbox(
    sidebar, height=10, exportselection=False, font=("Segoe UI", 12)
)
location_list.grid(row=1, column=0, sticky="ew")
for place in locations:
    location_list.insert(tk.END, place)
location_list.selection_set(0)

# Keep track of the selected location and which of the four charts is displayed.
selected_location = ""
chart_number = 0

# Add the chart heading, chart canvas, and chart navigation buttons.
chart_area = ttk.Frame(main_area)
chart_area.grid(row=0, column=1, sticky="nsew")
chart_area.columnconfigure(0, weight=1)
chart_area.rowconfigure(1, weight=1)
chart_heading = ttk.Label(chart_area, text="Select a location and click Analyze")
chart_heading.grid(row=0, column=0, pady=(0, 8))

# Create a pyplot figure and put a short instruction in its empty chart area.
figure = plt.figure(figsize=(7, 5))
plt.text(0.5, 0.5, "Your chart will appear here", ha="center", va="center")
plt.axis("off")
chart_canvas = FigureCanvasTkAgg(figure, master=chart_area)
chart_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
chart_canvas.draw()

# Display the current chart for the selected location using pyplot.
def show_chart():
    location_calls = calls[calls["Location"] == selected_location].copy()
    location_calls["Hour"] = pd.to_datetime(
        location_calls["Call_Time"], format="%H:%M"
    ).dt.hour
    plt.figure(figure.number)
    plt.clf()

    if chart_number == 0:
        # Count call types, shuffle their display order, and draw a bar chart.
        counts = location_calls["Call_Type"].value_counts()
        call_types = list(counts.index)
        random.shuffle(call_types)
        plt.bar(call_types, counts.reindex(call_types).values, color="steelblue")
        plt.title("Calls by Type in " + selected_location)
        plt.xlabel("Type of incident")
        plt.ylabel("Number of calls")
        plt.xticks(rotation=25, ha="right")
    elif chart_number == 1:
        # Count incidents in each hour and draw the hourly counts as a line chart.
        counts = (
            location_calls["Hour"]
            .value_counts()
            .reindex(range(24), fill_value=0)
            .sort_index()
        )
        plt.plot(counts.index, counts.values, marker="o", color="darkorange")
        plt.title("Calls by Hour in " + selected_location)
        plt.xlabel("Hour of day")
        plt.ylabel("Number of calls")
        plt.xticks(range(0, 24, 2))
        plt.xlim(0, 23)
        plt.grid(True, alpha=0.3)
    elif chart_number == 2:
        # Count each dispatched service by hour and draw one line per service.
        service_counts = location_calls.groupby(
            ["Hour", "Service_Dispatched"]
        ).size().unstack(fill_value=0)
        service_counts = service_counts.reindex(range(24), fill_value=0)
        service_counts = service_counts.reindex(
            columns=["Police", "Medical", "Fire"], fill_value=0
        )
        service_counts.plot(ax=plt.gca(), marker="o")
        plt.title("Services Dispatched by Hour in " + selected_location)
        plt.xlabel("Hour of day")
        plt.ylabel("Number of dispatches")
        plt.xticks(range(0, 24, 2))
        plt.xlim(0, 23)
        plt.grid(True, alpha=0.3)
        plt.legend(title="Service")
    else:
        # Group service counts into four parts of the day and draw grouped bars.
        periods = ["Night", "Morning", "Afternoon", "Evening"]
        location_calls["Time_Period"] = pd.cut(
            location_calls["Hour"], bins=[-1, 5, 11, 17, 23], labels=periods
        )
        grouped_counts = location_calls.groupby(
            ["Time_Period", "Service_Dispatched"], observed=False
        ).size().unstack(fill_value=0)
        grouped_counts = grouped_counts.reindex(index=periods, fill_value=0)
        grouped_counts = grouped_counts.reindex(
            columns=["Police", "Medical", "Fire"], fill_value=0
        )
        grouped_counts.plot(kind="bar", ax=plt.gca())
        plt.title("Service Dispatches by Time Period in " + selected_location)
        plt.xlabel("Time period")
        plt.ylabel("Number of dispatches")
        plt.xticks(rotation=0)
        plt.legend(title="Service")

    # Fit the chart into the available space and redraw it in the GUI.
    plt.tight_layout()
    chart_heading.configure(
        text=f"Chart {chart_number + 1} of 4 - {selected_location}"
    )
    chart_canvas.draw()


# Move to the next chart, wrapping around to the first chart when needed.
def next_chart():
    global chart_number
    chart_number = (chart_number + 1) % 4
    show_chart()


# Move to the previous chart, wrapping around to the last chart when needed.
def previous_chart():
    global chart_number
    chart_number = (chart_number - 1) % 4
    show_chart()


# Put Previous and Next buttons below the chart; enable them after analysis.
navigation = ttk.Frame(chart_area)
navigation.grid(row=2, column=0, pady=(10, 0))
previous_button = ttk.Button(
    navigation, text="Previous", command=previous_chart, state="disabled"
)
previous_button.grid(row=0, column=0, padx=5)
next_button = ttk.Button(
    navigation, text="Next", command=next_chart, state="disabled"
)
next_button.grid(row=0, column=1, padx=5)

# Show a two-second progress dialog with uneven progress updates.
def analyze():
    global selected_location, chart_number
    selection = location_list.curselection()
    if not selection:
        return

    selected_location = location_list.get(selection[0])
    chart_number = 0
    analyze_button.configure(state="disabled")
    loading_window = tk.Toplevel(window)
    loading_window.title("Analyzing")
    loading_window.geometry("350x120")
    loading_window.transient(window)
    loading_window.grab_set()
    ttk.Label(loading_window, text="Analyzing " + selected_location + "...").pack(
        padx=20, pady=(20, 10)
    )
    progress = ttk.Progressbar(
        loading_window, maximum=100, mode="determinate", length=180
    )
    progress.pack(padx=20, pady=(0, 20))

    # Finish the analysis when the two-second progress sequence is complete.
    def finish_analysis():
        progress["value"] = 100
        loading_window.destroy()
        analyze_button.configure(state="normal")
        previous_button.configure(state="normal")
        next_button.configure(state="normal")
        show_chart()

    # Use uneven steps that add up to two seconds.
    progress_steps = [(8, 250), (24, 350), (51, 400), (72, 450), (94, 550)]

    # Update the progress bar after each delay without blocking the GUI.
    def update_progress(step=0):
        value, delay = progress_steps[step]
        progress["value"] = value
        if step == len(progress_steps) - 1:
            loading_window.after(delay, finish_analysis)
        else:
            loading_window.after(delay, lambda: update_progress(step + 1))

    update_progress()


# Open a spreadsheet-like window showing all incidents at the selected location.
def show_incident_table():
    selection = location_list.curselection()
    if not selection:
        return

    location = location_list.get(selection[0])
    location_calls = calls[calls["Location"] == location]
    table_window = tk.Toplevel(window)
    table_window.title(f"Incidents in {location}")
    table_window.geometry("850x420")
    table_window.minsize(600, 300)
    table_window.columnconfigure(0, weight=1)
    table_window.rowconfigure(0, weight=1)

    # Create a resizable table with headings for each CSV column.
    table_frame = ttk.Frame(table_window, padding=10)
    table_frame.grid(row=0, column=0, sticky="nsew")
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)
    columns = ["Date", "Location", "Call_Type", "Call_Time", "Service_Dispatched"]
    incident_table = ttk.Treeview(
        table_frame, columns=columns, show="headings"
    )
    for column in columns:
        incident_table.heading(column, text=column.replace("_", " "))
        incident_table.column(column, width=145, anchor="w")

    # Add vertical and horizontal scrollbars for browsing all incident rows.
    vertical_scroll = ttk.Scrollbar(
        table_frame, orient="vertical", command=incident_table.yview
    )
    horizontal_scroll = ttk.Scrollbar(
        table_frame, orient="horizontal", command=incident_table.xview
    )
    incident_table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set,
    )
    incident_table.grid(row=0, column=0, sticky="nsew")
    vertical_scroll.grid(row=0, column=1, sticky="ns")
    horizontal_scroll.grid(row=1, column=0, sticky="ew")

    # Fill the table with the selected location's incident records.
    for incident in location_calls.itertuples(index=False, name=None):
        incident_table.insert("", tk.END, values=incident)


# Place the Analyze button beneath the list of locations.
analyze_button = ttk.Button(sidebar, text="Analyze", command=analyze)
analyze_button.grid(row=2, column=0, sticky="ew", pady=(10, 0))
table_button = ttk.Button(
    sidebar, text="View Incident Table", command=show_incident_table
)
table_button.grid(row=3, column=0, sticky="ew", pady=(8, 0))

# Show how many fictional records were loaded from the CSV.
status = ttk.Label(
    window,
    text=f"Loaded {len(calls)} incidents from the CSV file.",
    padding=(20, 8),
    anchor="w",
)
status.grid(row=2, column=0, sticky="ew")

# Start the Tkinter event loop so the app responds to user actions.
window.mainloop()
