import os

import plotly.express as px
import pandas as pd
import pytz
import streamlit as st
from komPYoot import API, TourType, TourOwner, Sport
import plotly.graph_objects as go
st.set_page_config(layout="wide")

# lets connect to komoot and get my actual runs
api = API()
api.login(os.environ["KOMOOOT_EMAIL"], os.environ["KOMOOOT_PASSWORD"])

tours = api.get_user_tours_list(
    tour_type=TourType.RECORDED,
    tour_owner=TourOwner.SELF,
    sport=Sport.RUNNING
)

tours_df = pd.json_normalize(tours)
tours_df["date"] = pd.to_datetime(tours_df["date"], format="ISO8601", utc=True).dt.tz_convert("Europe/Berlin")
tours_df["duration"] = pd.to_timedelta(tours_df["duration"], unit="s")
tours_df["duration[m]"] = tours_df["duration"].dt.total_seconds() / 60
tours_df["distance[km]"] = tours_df["distance"] / 1000
tours_df["time_in_motion"] = pd.to_timedelta(tours_df["time_in_motion"], unit="s")
tours_df["pace"] = tours_df["duration[m]"] / tours_df["distance[km]"] # may use time delta here and format ticks
tours_df["weekday"] = tours_df["date"].dt.day_name()



tours_df = tours_df[tours_df["date"] > pd.Timestamp("2024-01-01", tzinfo=pytz.timezone("Europe/Berlin"))]
tours_df.sort_values(by="date", ascending=True, inplace=True)
tours_df["#"] = range(1, len(tours_df) + 1)

# create a scatter plot showing distance vs. time and the color should encode the date
scatter = px.scatter(tours_df,
    x="distance[km]",
    y="pace",
    #symbol="sport",
    hover_data=["distance[km]", "duration[m]", "pace", "sport", "name", "date", "weekday"],
    color_continuous_scale="ylorrd_r",
    color="#",
    text="#",
    #size=10
)
scatter.update_layout(
    font=dict(family="Arial", size=10, color="black"),
)


scatter = go.Figure()
scatter.add_trace(
    go.Scatter(
        x=tours_df["distance[km]"],
        y=tours_df["pace"],
        mode="markers+text",
        #marker=dict(color=tours_df["date"],
        marker=dict(
            size=20,
            color=tours_df["#"],
            colorscale="ylorrd",
            #symbols=tours_df["weekday"],
        ),
        text=tours_df["#"],
        textfont=dict(color="black"),
        hoverinfo="text",
        name="Runs"
    ),

)
scatter.add_trace(go.Scatter(
    x=[21],
    y=[5],
    mode="markers",
    marker=dict(size=20, color="black", symbol="x"),
    name="Target"
) )
scatter.add_hline(y=5, line_color="grey", line_width=1, line_dash="dash")
scatter.add_vline(x=21, line_color="grey", line_width=1, line_dash="dash")
scatter.update_layout(
    xaxis=dict(title="Distance [km]"),
    yaxis=dict(title="Pace [min/km]", autorange="reversed"),
showlegend=True
)

line = px.line(tours_df, x="date", y="distance[km]", symbol="weekday", color="pace", markers=True)
#line = go.Scatter(
#    x=tours_df["date"],
#    y=tours_df["distance[km]"],
#    mode="lines+markers",
#    marker=dict(
#        color=tours_df["pace"],
#        size=tours_df["pace"],
#    )

line = go.Figure()
line.add_trace(
    go.Scatter(
        x=tours_df["date"],
        y=tours_df["distance[km]"],

    )
)

st.subheader("Runs: time vs distance")
st.plotly_chart(scatter, use_container_width=True)
st.plotly_chart(line, use_container_width=True)
#col2.subheader("Runs over time")
#col2.plotly_chart(line, use_container_width=True)
