import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme
import dash_table
import plotly.graph_objs as go

from helpers import clear_kraj, COLUMN_NAMES_MAPPING
from config import UNEMPLOYED_COL_NAME


def build_pct_line_figure(data_df, location_filter=None, year_filter=None):
    max_pct = 0.1

    lines = []
    if location_filter is not None:
        data_df = data_df[data_df["location"].isin(location_filter)]
    if year_filter is not None:
        data_df = data_df[data_df["year_month"].dt.year.isin(year_filter)]
    for location in data_df["location"].unique():
        name_short = clear_kraj(location)
        sl = data_df[data_df["location"] == location]
        max_pct_data = sl["unemployment_pct"].max()
        if max_pct_data > max_pct:
            max_pct = max_pct_data
        lines.append(
            go.Scatter(x=sl["year_month"], y=sl["unemployment_pct"],
                       mode="lines", name=name_short.strip(), )
        )

    line_fig = dict(data=lines, layout=dict(
        title='Procentuální nezaměstnanost v čase',

        yaxis=dict(tickformat=".2%", range=[0, max_pct]),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([

                    dict(count=6,
                         label='6y',
                         step='year',
                         stepmode='backward'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),

            type='date',
            title='Časová osa'
        )

    ))
    return line_fig


def build_age_bar_figure(data_df, location_filter=None, year_filter=None):

    bars = []
    if location_filter is not None:
        data_df = data_df[data_df["location"].isin(location_filter)]

    if year_filter is not None:
        data_df = data_df[data_df["year_month"].dt.year.isin(year_filter)]

    district_monthly = data_df.groupby(["location", "year_month"], as_index=False)[UNEMPLOYED_COL_NAME].sum()
    district_average_total = district_monthly.groupby("location")[UNEMPLOYED_COL_NAME].mean()

    for age_range in data_df["age_range"].unique():
        sl = data_df[data_df["age_range"] == age_range]
        district_average = sl.groupby("location")[UNEMPLOYED_COL_NAME].mean()
        pct = district_average/district_average_total
        bars.append(
            go.Bar(
                x=pct.index, y=pct,
                name=age_range,
                text=[f"{value:.0f} nezaměstnanosti kraje" for value in district_average],
                )
        )

    bar_fig = dict(data=bars, layout=dict(
        title='Distribuce nezaměstnaných dle věkové skupiny',
        xaxis=dict(title='Kraj'),
        barmode='stack',
        yaxis=dict(tickformat=".2%")
    ))
    return bar_fig


def build_abs_line_figure(data_df, location_filter=None, year_filter=None):

    lines = []
    if location_filter is not None:
        data_df = data_df[data_df["location"].isin(location_filter)]
    if year_filter is not None:
        data_df = data_df[data_df["year_month"].dt.year.isin(year_filter)]
    for location in data_df["location"].unique():

        name_short = clear_kraj(location)
        sl = data_df[data_df["location"] == location]
        lines.append(
            go.Scatter(x=sl["year_month"], y=sl[UNEMPLOYED_COL_NAME],
                       mode="lines", name=name_short.strip(), stackgroup='one', )
        )

    line_fig = dict(data=lines, layout=dict(
        title='Vývoj počtu nezaměstnaných',
        xaxis=dict(title='Časová osa')
    ))
    return line_fig


def get_data_table(total_cities_for_table):
    dash_table_columns = []
    for col in total_cities_for_table.columns:

        if col == "unemployment_pct":
            f = FormatTemplate.percentage(2)
            t = "numeric"
        elif col == "people_count" or col == UNEMPLOYED_COL_NAME:
            f = Format(
                precision=0,
                scheme=Scheme.fixed,
            )
            t = "numeric"
        else:
            f = {}
            t = "text"

        col_info = dict(name=COLUMN_NAMES_MAPPING[col],
                        id=col, type=t, format=f)

        dash_table_columns.append(col_info)

    dash_t = dash_table.DataTable(
        id="table",
        columns=dash_table_columns,
        data=total_cities_for_table.to_dict("rows"),
        # row_selectable="multi",
        # selected_rows=[],
        filtering=False,
        sorting=True,
        editable=False,
        style_as_list_view=True,
        pagination_mode="fe",
        pagination_settings={
            "displayed_pages": 1,
            "current_page": 0,
            "page_size": 35,
        },
        navigation="page",
    )
    return dash_t
