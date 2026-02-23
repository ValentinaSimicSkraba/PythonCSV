import pandas as pd
import plotly.express as px
import datetime as dt


# ---- Define your tasks ----
data = [
    {"Task": "Model update: integration into new twin", "Start": "2026-04-01", "Finish": "2026-04-24", "Phase": "Model integration"},
    {"Task": "FIM analysis and DOE on new twin", "Start": "2026-05-04", "Finish": "2026-06-01", "Phase": "Model integration"},
    {"Task": "Report preparation", "Start": "2026-06-01", "Finish": "2026-06-10", "Phase": "Model integration"},
    {"Task": "Vaccation", "Start": "2026-04-24", "Finish": "2026-05-04", "Phase": "Personal"},
    {"Task": "Vaje PTM", "Start": "2026-03-04", "Finish": "2026-03-05", "Phase": "Practicals"},
    {"Task": "Vaje PTM", "Start": "2026-03-11", "Finish": "2026-03-12", "Phase": "Practicals"},
    {"Task": "Vaje PTM", "Start": "2026-05-06", "Finish": "2026-05-07", "Phase": "Practicals"}

]

df = pd.DataFrame(data)

# Convert to datetime
df["Start"] = pd.to_datetime(df["Start"])
df["Finish"] = pd.to_datetime(df["Finish"])

# ---- Create Gantt ----
fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Phase"
)

fig.update_yaxes(autorange="reversed")  # Top task at top

# ---- Make axis start at 1st of month, end at end of month ----
start_month = df["Start"].min().to_period("M").start_time
end_month = df["Finish"].max().to_period("M").end_time.normalize() + pd.Timedelta(days=1)

fig.update_xaxes(range=[start_month, end_month])

# ---- Month ticks: always on the 1st ----
fig.update_xaxes(
    dtick="M1",
    tickformat="%b %Y",
    ticks="outside",
    showgrid=True,
    gridwidth=1
)

# ---- Weekly lines (Mondays) for easy week counting ----
week_starts = pd.date_range(start=start_month, end=end_month, freq="W-MON")
for d in week_starts:
    fig.add_vline(x=d, line_width=1, opacity=0.25)

# ---- Milestones ----
milestones = {
    "Final Twin from RWU": "2026-04-01",
    "ALARMBOT face-to-face meeting": "2026-06-10"
}

# Give the figure more headroom so labels above the plot are not clipped
fig.update_layout(
    margin=dict(t=140)  # increase top margin (adjust 120–180 as needed)
)

# Style settings
milestone_line_color = "crimson"
milestone_text_color = "crimson"
milestone_font_size = 16

# Add lines + labels
for i, (name, date) in enumerate(milestones.items()):
    x_date = pd.to_datetime(date)

    # Vertical line
    fig.add_vline(
        x=x_date,
        line_width=3,
        line_dash="dash",
        line_color=milestone_line_color
    )

    # Label above the plotting area (staggered to avoid overlap)
    fig.add_annotation(
        x=x_date,
        y=1.08 + i * 0.06,   # above chart; stagger labels
        yref="paper",
        text=name,
        showarrow=False,
        font=dict(size=milestone_font_size, color=milestone_text_color),
        align="center"
    )
    # Add horizontal separator lines between tasks
    for i in range(len(df["Task"])):
        fig.add_hline(
            y=i - 0.5,
            line_width=1,
            line_color="lightgray",
            opacity=0.5
        )
        
        
# ---- Countdown target date ----
target_date = pd.to_datetime("2026-06-10")   # <-- change this
today = pd.to_datetime(dt.date.today())

days_left = (target_date - today).days
weeks_left = days_left / 7

# Clamp if date is past
if days_left >= 0:
    countdown_text = f"⏳ {days_left} days left ({weeks_left:.1f} weeks)\n→ {target_date.date()}"
else:
    countdown_text = f"✅ Target passed {abs(days_left)} days ago\n({target_date.date()})"

# Put it in the top-right fringe (outside plot area)
fig.add_annotation(
    x=1.01, y=1.02,
    xref="paper", yref="paper",
    text=countdown_text,
    showarrow=False,
    align="left",
    font=dict(size=16, color="crimson"),
    bordercolor="crimson",
    borderwidth=2,
    borderpad=8,
    bgcolor="rgba(255,255,255,0.85)"
)
# ---- Define timeline range ----
today = pd.to_datetime(dt.date.today())
end_date = pd.to_datetime("2026-06-11")

fig.update_xaxes(
    range=[today, end_date]
)
# Add right/top margin so it doesn't get clipped
fig.update_layout(margin=dict(r=220, t=140))
# ---- Layout ----
fig.update_layout(
    title="Project Timeline",
    xaxis_title="Date",
    yaxis_title="",
    template="plotly_white",
    plot_bgcolor="#f7f9fc",     # inside chart area
    paper_bgcolor="#e9eef5",    # outside background
)

fig.show()