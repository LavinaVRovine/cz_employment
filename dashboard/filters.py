from helpers import clear_kraj
import dash_core_components as dcc


def get_time_picker(total_district_df):

    years = total_district_df["year_month"].dt.year.unique()
    time_picker = dcc.RangeSlider(
        marks={int(i): "Rok {}".format(i) for i in years},
        min=years.min(),
        max=years.max(),
        value=list(years),
        id="year-range"
    )
    return time_picker


def get_region_checker(total_district_df):

    region_dropdown = dcc.Dropdown(
        options=[{"label": clear_kraj(key), "value": key} for key in total_district_df["location"].unique()],
        value=total_district_df["location"].unique(),
        id="region-dropbox",
        multi=True, clearable=True, placeholder="Zvolte kraj..."

    )
    return region_dropdown
