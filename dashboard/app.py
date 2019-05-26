import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from config import UNEMPLOYED_COL_NAME, UA_ID, DEBUG
from dashboard.data_loader import load_totals_data, load_age_data, load_table_data
from dashboard.custom_css import tab_selected_style, tabs_styles, tab_style
from db_handle import test_engine
from dashboard.visuals import build_pct_line_figure, build_age_bar_figure, build_abs_line_figure, get_data_table
from dashboard.filters import get_region_checker, get_time_picker

"""
ideas: pridat pocty pracovnich pozict, pridat dalsi veci co mam nascrapovane
"""
# TODO: date slider still sux
# TODO: heroku problem - app has around 600MB, 512 is max
engine = test_engine()

app = dash.Dash(__name__)

app.scripts.config.serve_locally = False
app.scripts.append_script({
    'external_url': f'https://www.googletagmanager.com/gtag/js?id=UA-{UA_ID}'
})

app.scripts.append_script({
    'external_url': '/assets/gtag.js'
})


# needed to dynamically generate filtered graphs in Tabs, because the graph does not exists without tab being selected
app.config['suppress_callback_exceptions'] = True
server = app.server
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# data
total_district_df, total_cities_df = load_totals_data()
age_district_df, age_cities_df = load_age_data()
total_cities_for_table = load_table_data(total_cities_df)

# visuals
line_figure = build_abs_line_figure(total_district_df)
age_figure = build_age_bar_figure(age_district_df)
pct_figure = build_pct_line_figure(total_district_df)
# filters
time_picker = get_time_picker(total_district_df)
region_dropdown = get_region_checker(total_district_df)
dash_t = get_data_table(total_cities_for_table)


layout = html.Div([
    html.Div(className="container-fluid", style={"padding-left": "15px", "padding-right": "15px"}, children=[
        html.Div(html.H3(
            "Statistiky nezaměstnanosti v ČR", style={"text-align": "center", "vertical-align": "middle"}
        ), className="row"),
        html.Div(className="row", children=[
            html.Div(className="row", children=[
                html.Div(region_dropdown),
                html.Br(),
                html.Div(className="one column"),
                html.Div(time_picker, className="ten columns", ),

                html.Br()
            ], ),
            html.Br(),
            html.Div(className="row", children=[
                html.Div([
                    dcc.Tabs(id="tabs-example", value='tab-3-example', children=[
                        dcc.Tab(label='Vývoj procentuální nezaměstnanost', value='tab-3-example',
                                style=tab_style, selected_style=tab_selected_style
                                ),
                        dcc.Tab(label='Vývoj absolutní nezaměsnanosti', value='tab-1-example',
                                style=tab_style, selected_style=tab_selected_style
                                ),
                        dcc.Tab(label='Distribuce dle věkové skupiny', value='tab-2-example',
                                style=tab_style, selected_style=tab_selected_style
                                ),
                    ], style=tabs_styles),
                    html.Div(id='tabs-content')
                ], ),

            ], style={"margin-top": "15px"}),

            html.Div(className="row eleven columns", children=[
                html.H6("Základní statistiky (průměr zvoleného období)",
                        style={"text-align": "center", "vertical-align": "middle"}),
                html.Div(dash_t)]
                     ),

        ])
    ]),
    html.Div(className="row", children=[
        html.Footer(children=[
            html.Div(className="row",
                     style={"padding-top": "25px"},
                     children=[
                         html.A("Statistiky nezaměstnanosti získány z mpsv",
                                href="https://portal.mpsv.cz/sz/stat/nz/qrt", className="six columns",
                                style={"vertical-align": "right", "text-align": "right"}),
                         html.A("Statistiky počtu obyvatel získány z czso",
                                href="https://www.czso.cz/csu/czso/databaze-demografickych-udaju-za-obce-cr",
                                className="six columns", style={"vertical-align": "left", "text-align": "left"}),
                     ]),
            html.Div(children=[
                dcc.Markdown("[Made] (https://github.com/LavinaVRovine/cz_employment) for fun in Brno, Czechia 2019"),
                html.A("Pavel Klammert", href="http://www.klammert.cz/")
            ], style={"vertical-align": "center", "text-align": "center"})
        ])
    ])
])

app.layout = layout
app.title = "Statistiky nezaměstnanosti v ČR"


@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='region-dropbox', component_property='value'),
     Input(component_id="year-range", component_property="value")]
)
def update_table(region_values, year_values):
    data_df = total_cities_df
    if region_values is not None:
        data_df = data_df[data_df["district"].isin(region_values)]
    if year_values is not None:
        data_df = data_df[data_df["year"].isin(year_values)]
    # people living in city are per city/year, so we get rid of that
    y_m_stats_per_location = data_df.groupby(
        ["district", "location", "year_month"], as_index=False
    )["people_count", "unemployment_count"].agg({"people_count": "sum", "unemployment_count": "mean"})

    table_data = y_m_stats_per_location.groupby(["district", "location"], as_index=False)[
        "people_count", UNEMPLOYED_COL_NAME].mean()
    table_data["unemployment_pct"] = table_data[UNEMPLOYED_COL_NAME] / table_data[
        "people_count"]

    return table_data.to_dict("rows")


@app.callback(
    Output(component_id='unemployment-lines', component_property='figure'),
    [Input(component_id='region-dropbox', component_property='value'),
     Input(component_id="year-range", component_property="value"), ]
)
def update_line(region_values, year_values):
    fig = build_abs_line_figure(total_district_df, region_values, year_values)

    return fig


@app.callback(
    Output(component_id='graph-2-tabs', component_property='figure'),
    [Input(component_id='region-dropbox', component_property='value'),
     Input(component_id="year-range", component_property="value"), ]
)
def update_age_bars(region_values, year_values):
    fig = build_age_bar_figure(age_district_df, region_values, year_values)
    return fig


@app.callback(
    Output(component_id='graph-3-tabs', component_property='figure'),
    [Input(component_id='region-dropbox', component_property='value'),
     Input(component_id="year-range", component_property="value"), ]
)
def update_pct_line(region_values, year_values):
    fig = build_pct_line_figure(total_district_df, region_values, year_values)
    return fig


# handles tabs
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1-example':
        return html.Div([dcc.Graph(id='unemployment-lines', figure=line_figure,)]),
    elif tab == 'tab-2-example':
        return html.Div(dcc.Graph(id='graph-2-tabs', figure=age_figure, )),
    elif tab == 'tab-3-example':
        return html.Div(dcc.Graph(id='graph-3-tabs', figure=pct_figure, )),


if __name__ == '__main__':
    app.server.run(debug=DEBUG)
