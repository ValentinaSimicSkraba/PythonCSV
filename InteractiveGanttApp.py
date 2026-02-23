# app.py
import pandas as pd
import plotly.express as px
import datetime as dt
import os

from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update

# -----------------------------
# Data (your tasks)
# -----------------------------
data = [
    {"Task": "Model update: integration into new twin", "Start": "2026-04-01", "Finish": "2026-04-24", "Phase": "Model integration"},
    {"Task": "FIM analysis and DOE on new twin", "Start": "2026-05-04", "Finish": "2026-06-01", "Phase": "Model integration"},
    {"Task": "Report preparation", "Start": "2026-06-01", "Finish": "2026-06-10", "Phase": "Model integration"},
    {"Task": "Vaccation", "Start": "2026-04-24", "Finish": "2026-05-04", "Phase": "Personal"},
    {"Task": "Vaje PTM", "Start": "2026-03-04", "Finish": "2026-03-05", "Phase": "Practicals"},
    {"Task": "Vaje PTM", "Start": "2026-03-11", "Finish": "2026-03-12", "Phase": "Practicals"},
    {"Task": "Vaje PTM", "Start": "2026-05-06", "Finish": "2026-05-07", "Phase": "Practicals"},
]

df0 = pd.DataFrame(data)
df0["Start"] = pd.to_datetime(df0["Start"])
df0["Finish"] = pd.to_datetime(df0["Finish"])

# -----------------------------
# Settings (your milestones + countdown)
# -----------------------------
milestones = {
    "Final Twin from RWU": "2026-04-01",
    "ALARMBOT face-to-face meeting": "2026-06-10",
}

TARGET_DATE = pd.to_datetime("2026-06-10")     # countdown target
END_DATE   = pd.to_datetime("2026-06-20")      # axis end (exclusive-ish)

MILESTONE_COLOR = "crimson"
MILESTONE_FONT_SIZE = 18

TASKS_CSV = "gantt_tasks.csv"
def write_csv(records):
    pd.DataFrame(records).to_csv(TASKS_CSV, index=False)
if os.path.exists(TASKS_CSV):
    df0 = pd.read_csv(TASKS_CSV)
else:
    df0 = pd.DataFrame(data)
    
def wrap_milestone(s: str, width: int = 22, max_lines: int = 2) -> str:
    return wrap_label(s, width=width, max_lines=max_lines)  # returns "line1<br>line2"

df0["Start"] = pd.to_datetime(df0["Start"])
df0["Finish"] = pd.to_datetime(df0["Finish"])
def wrap_label(s: str, width: int = 28, max_lines: int = 2) -> str:
    # simple word-wrap into at most 2 lines
    words = s.split()
    lines, cur = [], []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) <= width:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
            if len(lines) >= max_lines - 1:
                break
    if cur:
        lines.append(" ".join(cur))
    # If we truncated, add ellipsis
    used_words = " ".join(lines).split()
    if len(used_words) < len(words):
        lines[-1] = lines[-1].rstrip() + "…"
    return "<br>".join(lines)

# -----------------------------
# Figure builder (keeps your styling)
# -----------------------------
def make_figure(df: pd.DataFrame):
    df = df.copy()
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["TaskLabel"] = df["Task"].apply(lambda s: wrap_label(s, width=30, max_lines=2))
    
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="TaskLabel",
        color="Phase"
    )

    fig.update_yaxes(autorange="reversed")

    # Axis range: today -> END_DATE
    today = pd.Timestamp.today().normalize()
    fig.update_xaxes(range=[today, END_DATE])

    # Month ticks on 1st
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
        ticks="outside",
        showgrid=True,
        gridwidth=1
    )

    # Weekly lines (Mondays)
    week_starts = pd.date_range(start=today, end=END_DATE, freq="W-MON")
    for d in week_starts:
        fig.add_vline(x=d, line_width=1, opacity=0.25)

    # Milestones + labels
    for j, (name, date) in enumerate(milestones.items()):
        x_date = pd.to_datetime(date)

        fig.add_vline(
            x=x_date,
            line_width=3,
            line_dash="dash",
            line_color=MILESTONE_COLOR
        )

        fig.add_annotation(
            x=x_date,
            y=1.08 + j * 0.06,
            yref="paper",
            text=wrap_milestone(name, width=22, max_lines=2),            
            showarrow=False,
            font=dict(size=MILESTONE_FONT_SIZE, color=MILESTONE_COLOR),
            align="center",
            bordercolor="rgba(0,0,0,0)",   # optional
        )

    # Horizontal separators (added ONCE — not inside milestone loop)
    # Note: with categorical y this is sometimes finicky depending on Plotly version.
    # If you see odd behavior, switch to row shading instead.
    for i in range(len(df["Task"])):
        fig.add_hline(
            y=i - 0.5,
            line_width=1,
            line_color="lightgray",
            opacity=0.5
        )

    # Countdown box (fringe)
    days_left = (TARGET_DATE - today).days
    weeks_left = days_left / 7

    if days_left >= 0:
        countdown_text = f"⏳ {days_left} days left ({weeks_left:.1f} weeks)<br>→ {TARGET_DATE.date()}"
    else:
        countdown_text = f"✅ Target passed {abs(days_left)} days ago<br>({TARGET_DATE.date()})"



    # Layout / background like your script
    fig.update_layout(
    title="Project Timeline",
    xaxis_title="Date",
    yaxis_title="",
    template="plotly_white",
    plot_bgcolor="#f7f9fc",
    paper_bgcolor="#e9eef5",

    # give space to labels on the left, but DON'T kill the plot area
    margin=dict(l=220, r=40, t=170, b=60),

    showlegend=False,
    )

    return fig


# -----------------------------
# Dash app (edit Start/Finish)
# -----------------------------
app = Dash(__name__)
app.title = "Editable Gantt"

def df_to_store(df: pd.DataFrame):
    out = df.copy()
    out["Start"] = out["Start"].dt.strftime("%Y-%m-%d")
    out["Finish"] = out["Finish"].dt.strftime("%Y-%m-%d")
    return out.to_dict("records")

def store_to_df(records):
    df = pd.DataFrame(records)
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    return df

app.layout = html.Div(
    style={"fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"},
    children=[
        dcc.Store(id="store", data=df_to_store(df0)),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "3.2fr 1fr", "gap": "14px", "alignItems": "start"},
            children=[
                dcc.Graph(id="gantt", figure=make_figure(df0),style={"height": "820px"}, config={"displayModeBar": True}),

                html.Div(
                    style={"background": "rgba(255,255,255,0.75)", "padding": "12px", "borderRadius": "12px"},
                    children=[
                        html.Div(id="side_info", style={
                            "background": "#f4f6fa",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "marginBottom": "12px"
                        }),
                        html.H3("Edit a task", style={"marginTop": 0}),
                        html.Div("Pick a row in the table, then adjust Start/Finish and click Update."),
                        html.Button("Save to CSV", id="save_btn", n_clicks=0, style={"padding": "8px 12px"}),
                        html.Button(
                            "Delete selected",
                            id="delete_btn",
                            n_clicks=0,
                            style={"padding": "8px 12px", "background": "#ffe5e5", "border": "1px solid #ffb3b3"}
                        ),
                        dash_table.DataTable(
                            id="table",
                            columns=[
                                {"name": "Task", "id": "Task"},
                                {"name": "Start", "id": "Start"},
                                {"name": "Finish", "id": "Finish"},
                                {"name": "Phase", "id": "Phase"},
                            ],
                            data=df_to_store(df0),
                            row_selectable="single",
                            selected_rows=[0],
                            style_table={"overflowX": "auto", "maxHeight": "340px", "overflowY": "auto"},
                            style_cell={"fontSize": 12, "padding": "6px", "whiteSpace": "normal", "height": "auto"},
                            style_header={"fontWeight": "600"},
                        ),

                        html.Hr(),

                        html.Label("Selected task"),
                        dcc.Dropdown(id="task_dd", clearable=False),

                        html.Label("Task name"),
                        dcc.Input(
                            id="task_name_input",
                            type="text",
                            style={"width": "100%", "marginBottom": "10px"}
                        ),
                        
                        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"}, children=[
                            html.Div([
                                html.Label("Start"),
                                dcc.DatePickerSingle(id="start_dp"),
                            ]),
                            html.Div([
                                html.Label("Finish"),
                                dcc.DatePickerSingle(id="finish_dp"),
                            ]),
                        ]),

                        html.Div(style={"marginTop": "10px", "display": "flex", "gap": "10px"}, children=[
                            html.Button("Update", id="update_btn", n_clicks=0, style={"padding": "8px 12px"}),
                            html.Button("Add new task", id="add_btn", n_clicks=0, style={"padding": "8px 12px"}),
                        ]),

                        html.Div(id="msg", style={"marginTop": "10px", "color": "#444"})
                    ]
                ),
            ]
        )
    ]
)

@app.callback(
    Output("side_info", "children"),
    Input("store", "data"),
)
def update_side_panel(records):
    today = pd.Timestamp.today().normalize()
    days_left = (TARGET_DATE - today).days
    weeks_left = days_left / 7

    if days_left >= 0:
        countdown = f"{days_left} days left ({weeks_left:.1f} weeks)"
    else:
        countdown = f"Target passed {abs(days_left)} days ago"

    return [
        html.H4("Countdown"),
        html.Div(f"→ {TARGET_DATE.date()}"),
        html.Div(countdown, style={"color": "crimson", "fontWeight": "600"}),
        html.Hr(),
        html.H4("Phases"),
        html.Ul([
            html.Li("Model integration", style={"color": "#636EFA"}),
            html.Li("Personal", style={"color": "#EF553B"}),
            html.Li("Practicals", style={"color": "#00CC96"}),
        ])
    ]


# Populate dropdown from store + sync when table selection changes
@app.callback(
    Output("task_dd", "options"),
    Output("task_dd", "value"),
    Output("task_name_input", "value"),
    Output("start_dp", "date"),
    Output("finish_dp", "date"),
    Input("store", "data"),
    Input("table", "selected_rows"),
)
def sync_editor(records, selected_rows):
    df = pd.DataFrame(records)
    options = [{"label": t, "value": t} for t in df["Task"].tolist()]

    if not selected_rows:
        sel_idx = 0
    else:
        sel_idx = selected_rows[0]
        if sel_idx >= len(df):
            sel_idx = 0

    row = df.iloc[sel_idx]
    return options, row["Task"], row["Task"], row["Start"], row["Finish"]


# Populate dropdown from store + sync when table selection changes


# Update selected row (rename + dates) — SINGLE update callback
@app.callback(
    Output("store", "data"),
    Output("table", "data"),
    Output("msg", "children"),
    Input("update_btn", "n_clicks"),
    State("store", "data"),
    State("table", "selected_rows"),
    State("task_name_input", "value"),
    State("start_dp", "date"),
    State("finish_dp", "date"),
    prevent_initial_call=True
)
def update_selected_task(n, records, selected_rows, new_name, start_date, finish_date):
    if not selected_rows:
        return no_update, no_update, "Select a row in the table first."

    if new_name is None or str(new_name).strip() == "":
        return no_update, no_update, "Task name cannot be empty."

    if start_date is None or finish_date is None:
        return no_update, no_update, "Please set both Start and Finish."

    start = pd.to_datetime(start_date)
    finish = pd.to_datetime(finish_date)
    if finish < start:
        return no_update, no_update, "Finish must be on/after Start."

    idx = selected_rows[0]
    df = pd.DataFrame(records)
    if idx < 0 or idx >= len(df):
        return no_update, no_update, "Selected row out of range."

    old_name = df.loc[idx, "Task"]
    df.loc[idx, "Task"] = str(new_name).strip()
    df.loc[idx, "Start"] = start.strftime("%Y-%m-%d")
    df.loc[idx, "Finish"] = finish.strftime("%Y-%m-%d")

    updated = df.to_dict("records")
    write_csv(updated)
    return updated, updated, f"Updated row {idx+1}: '{old_name}' → '{df.loc[idx,'Task']}'"


# Add a new task
@app.callback(
    Output("store", "data", allow_duplicate=True),
    Output("table", "data", allow_duplicate=True),
    Output("table", "selected_rows", allow_duplicate=True),
    Output("msg", "children", allow_duplicate=True),
    Input("add_btn", "n_clicks"),
    State("store", "data"),
    prevent_initial_call=True
)
def add_task(n, records):
    df = pd.DataFrame(records)
    today = pd.Timestamp.today().normalize()

    new_row = {
        "Task": f"New task {len(df) + 1}",
        "Start": today.strftime("%Y-%m-%d"),
        "Finish": (today + pd.Timedelta(days=7)).strftime("%Y-%m-%d"),
        "Phase": "Model integration",
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    updated = df.to_dict("records")
    write_csv(updated)

    new_idx = len(df) - 1
    return updated, updated, [new_idx], "Added a new task. Rename it and adjust dates."


# ---- Save button ----
@app.callback(
    Output("msg", "children", allow_duplicate=True),
    Input("save_btn", "n_clicks"),
    State("store", "data"),
    prevent_initial_call=True
)
def save_to_csv_cb(n, records):
    write_csv(records)
    return f"Saved {len(records)} tasks to {TASKS_CSV}"

# ---- delete button ------
@app.callback(
    Output("store", "data", allow_duplicate=True),
    Output("table", "data", allow_duplicate=True),
    Output("table", "selected_rows", allow_duplicate=True),
    Output("msg", "children", allow_duplicate=True),
    Input("delete_btn", "n_clicks"),
    State("store", "data"),
    State("table", "selected_rows"),
    prevent_initial_call=True
)
def delete_selected_task(n, records, selected_rows):
    if not selected_rows:
        return no_update, no_update, no_update, "Select a row to delete."

    df = pd.DataFrame(records)
    idx = selected_rows[0]

    if idx < 0 or idx >= len(df):
        return no_update, no_update, no_update, "Selected row out of range."

    deleted_name = df.loc[idx, "Task"]

    df = df.drop(index=idx).reset_index(drop=True)
    updated = df.to_dict("records")

    # pick next selected row
    if len(df) == 0:
        new_sel = []
        msg = f"Deleted '{deleted_name}'. No tasks left."
    else:
        new_sel = [min(idx, len(df) - 1)]
        msg = f"Deleted '{deleted_name}'."

    # OPTIONAL: persist automatically
    write_csv(updated)

    return updated, updated, new_sel, msg

# ---- Redraw gantt whenever store changes ----
@app.callback(
    Output("gantt", "figure"),
    Input("store", "data"),
)
def redraw(records):
    df = store_to_df(records)
    return make_figure(df)


if __name__ == "__main__":
    app.run(debug=True)