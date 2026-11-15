"""A simple Tkinter app for exploring fictional 911 call data."""

# Import Tkinter for the window and pandas for reading and grouping the data.
from pathlib import Path
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
window.geometry("1000x650")
window.minsize(800, 500)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

# Add the project title across the top of the window.
title = ttk.Label(window, text="911 Call Analysis", font=("Segoe UI", 22, "bold"))
title.grid(row=0, column=0, sticky="w", padx=20, pady=15)

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
location_list = tk.Listbox(sidebar, height=10, exportselection=False)
location_list.grid(row=1, column=0, sticky="ew")
for place in locations:
    location_list.insert(tk.END, place)
location_list.selection_set(0)

# Keep track of the selected location and which of the two charts is displayed.
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
    plt.figure(figure.number)
    plt.clf()

    if chart_number == 0:
        # Count each call type and draw the counts as a bar chart.
        counts = location_calls["Call_Type"].value_counts()
        plt.bar(counts.index, counts.values, color="steelblue")
        plt.title("Calls by Type in " + selected_location)
        plt.xlabel("Type of incident")
        plt.ylabel("Number of calls")
        plt.xticks(rotation=25, ha="right")
    else:
        # Count incidents in each hour and draw the hourly counts as a line chart.
        hours = pd.to_datetime(location_calls["Call_Time"], format="%H:%M").dt.hour
        counts = hours.value_counts().reindex(range(24), fill_value=0).sort_index()
        plt.plot(counts.index, counts.values, marker="o", color="darkorange")
        plt.title("Calls by Hour in " + selected_location)
        plt.xlabel("Hour of day")
        plt.ylabel("Number of calls")
        plt.xticks(range(0, 24, 2))
        plt.xlim(0, 23)
        plt.grid(True, alpha=0.3)

    # Fit the chart into the available space and redraw it in the GUI.
    plt.tight_layout()
    chart_heading.configure(
        text=f"Chart {chart_number + 1} of 2 - {selected_location}"
    )
    chart_canvas.draw()


# Move to the next chart, wrapping around to the first chart when needed.
def next_chart():
    global chart_number
    chart_number = (chart_number + 1) % 2
    show_chart()


# Move to the previous chart, wrapping around to the last chart when needed.
def previous_chart():
    global chart_number
    chart_number = (chart_number - 1) % 2
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

# Show a progress dialog for five seconds, with uneven progress updates.
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
        loading_window, maximum=100, mode="determinate", length=300
    )
    progress.pack(padx=20, pady=(0, 20))

    # Finish the analysis when the five-second progress sequence is complete.
    def finish_analysis():
        progress["value"] = 100
        loading_window.destroy()
        analyze_button.configure(state="normal")
        previous_button.configure(state="normal")
        next_button.configure(state="normal")
        show_chart()

    # Use different progress values and delays to make the loading feel natural.
    progress_values = [5, 14, 22, 37, 44, 61, 73, 81, 96]
    progress_delays = [300, 450, 650, 400, 700, 450, 800, 550, 700]

    # Update the progress bar after each delay without blocking the GUI.
    def update_progress(step=0):
        progress["value"] = progress_values[step]
        if step == len(progress_values) - 1:
            loading_window.after(progress_delays[step], finish_analysis)
        else:
            loading_window.after(
                progress_delays[step], lambda: update_progress(step + 1)
            )

    update_progress()


# Place the Analyze button beneath the list of locations.
analyze_button = ttk.Button(sidebar, text="Analyze", command=analyze)
analyze_button.grid(row=2, column=0, sticky="ew", pady=(10, 0))

# Show how many fictional records were loaded from the CSV.
status = ttk.Label(
    window,
    text=f"Loaded {len(calls)} fictional incidents from the CSV file.",
    padding=(20, 8),
    anchor="w",
)
status.grid(row=2, column=0, sticky="ew")

# Start the Tkinter event loop so the app responds to user actions.
window.mainloop()
