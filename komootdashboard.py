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

# create a scatter plot showing distance vs. time and the color should encode the date
scatter = px.scatter(tours_df,
    x="distance[km]",
    y="duration[m]",
    #symbol="sport",
    hover_data=["distance[km]", "duration[m]", "pace", "sport", "name", "date", "weekday"],
    color="pace",
    color_continuous_scale="ylorrd_r",
    size="pace",

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
#)
col1, col2 = st.columns([1, 1])


col1.subheader("Runs: time vs distance")
col1.plotly_chart(scatter, use_container_width=True)

col2.subheader("Runs over time")
col2.plotly_chart(line, use_container_width=True)
