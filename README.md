# 911 Call Analysis

A simple Class 12 project dashboard built with Python and Tkinter. It loads a
fictional dataset of 700 911-call incidents from `data/911_calls.csv` into a
pandas DataFrame. Each incident has a date, location, call type, call time, and
one dispatched service. Select a location in the sidebar and click **Analyze**
to view charts for call type, incidents by hour, and dispatched services by
hour, plus a grouped comparison of services by time of day. Call-type bars are
shown in a shuffled order. Use **Previous** and **Next** to switch between
charts, or **View Incident Table** to open a scrollable table for the selected
location.

## Run the app

1. Install Python 3.9 or newer.
2. Install pandas with `python -m pip install -r requirements.txt`.
3. Start the dashboard with `python app.py`.

Tkinter is included with most standard Python installations. If it is missing,
install the Tk support package provided for your Python distribution.

Resize or maximize the window as needed. The sample records are fictional and
the location-specific time patterns are illustrative, not real emergency
statistics.
