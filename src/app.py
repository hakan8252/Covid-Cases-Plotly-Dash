import pandas as pd  # (version 1.0.0)
import plotly  # (version 4.5.4) pip install plotly==4.5.4
import plotly.express as px

import dash  # (version 1.9.1) pip install dash==1.9.1
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table, dcc, html, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# ---------------------------------------------------------------
# Taken from https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases
url = 'https://raw.githubusercontent.com/hakan8252/Covid-Cases-Plotly-Dash/main/COVID-19-geographic-disbtribution-worldwide-2020-03-29.xlsx'
df = pd.read_excel(url)
#
dff = df.groupby('countriesAndTerritories', as_index=False)[['deaths', 'cases']].sum()
print(dff[:5])
# ---------------------------------------------------------------

# # Define dropdown options
dropdown_options = [
    {'label': 'Deaths', 'value': 'deaths'},
    {'label': 'Cases', 'value': 'cases'}
]

controls = dbc.Card([

    html.Div([

        dbc.Button(
            "Click For Reset", id="reset-button", className="me-2 mb-2", n_clicks=0,
            style={"background-color": "#3d5a80"}
        ),
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=6,
            # page_action='none',
            # style_cell={
            # 'whiteSpace': 'normal'
            # },
            # fixed_rows={ 'headers': True, 'data': 0 },
            # virtualization=False,
            style_cell_conditional=[
                {'if': {'column_id': 'countriesAndTerritories'},
                 'width': '40%', 'textAlign': 'left'},
                {'if': {'column_id': 'deaths'},
                 'width': '30%', 'textAlign': 'left'},
                {'if': {'column_id': 'cases'},
                 'width': '30%', 'textAlign': 'left'},
            ],
        ),
    ]),

    html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='dropdown_pie',
                    options=dropdown_options,
                    value=None,
                    placeholder="Select an option for Pie Chart",
                    clearable=False,
                    multi=False,
                    style={
                        'backgroundColor': 'white',
                        "color": "#3ad0e0"
                    }
                ),
                width=2
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='dropdown_line',
                    options=dropdown_options,
                    value=None,
                    placeholder="Select an option for Line Chart",
                    clearable=False,
                    multi=False,
                    style={
                        'backgroundColor': 'white',
                        "color": "#3ad0e0"
                    }
                ),
                width=2
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='dropdown_bar',
                    options=dropdown_options,
                    value=None,
                    placeholder="Select an option for Bar Chart",
                    clearable=False,
                    multi=False,
                    style={
                        'backgroundColor': 'white',
                        "color": "#3ad0e0"
                    }
                ),
                width=2
            ),
        ])
    ])

], body=True, color="rgba(74, 104, 106, 0.7)")

graphics = dbc.Card([
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-chart"), md=4),
        dbc.Col(dcc.Graph(id="line-chart"), md=4),
        dbc.Col(dcc.Graph(id="bar-chart"), md=4),
    ], )
], body=True, className="mt-3", color="rgba(230, 240, 240,0.7)")

app.layout = dbc.Container(
    [
        html.H1("Deaths/Cases Covid"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(graphics, md=12),
            ],
            align="center",
        ),
    ],
    fluid=True,
)


# ------------------------------------------------------------------
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('datatable_id', 'selected_rows'),
     Input('dropdown_pie', 'value'),
     Input('dropdown_line', 'value'),
     Input('dropdown_bar', 'value')]
)
def update_data(chosen_rows, selected_pie, selected_line, selected_bar):
    # Set a custom color sequence for discrete variables
    dark_colors = ["#3d5a80", "#98c1d9", "#e0fbfc", "#ee6c4d", "#293241"]

    if len(chosen_rows) == 0:
        df_filterd = dff[dff['countriesAndTerritories'].isin(['China', 'Iran', 'Spain', 'Italy'])]
    else:
        print(chosen_rows)
        df_filterd = dff[dff.index.isin(chosen_rows)]

    pie_chart = px.pie(
        data_frame=df_filterd,
        names="countriesAndTerritories",
        values=selected_pie,
        hole=.3,
        labels={'countriesAndTerritories': 'Countries'},
        color_discrete_sequence=dark_colors
    )
    pie_chart.update_layout(title=f"{selected_pie}: Pie", template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)", title_font_color="black", font_color="black")

    # extract list of chosen countries
    list_chosen_countries = df_filterd['countriesAndTerritories'].tolist()
    # filter original df according to chosen countries
    # because original df has all the complete dates
    df_line = df[df['countriesAndTerritories'].isin(list_chosen_countries)]

    line_chart = px.line(
        data_frame=df_line,
        x='dateRep',
        y=selected_line,
        color='countriesAndTerritories',
        labels={'countriesAndTerritories': 'Countries', 'dateRep': 'date'},
        color_discrete_sequence=dark_colors
    )
    line_chart.update_layout(uirevision='foo', title=f"{selected_line}: Line", template="plotly_dark",
                             plot_bgcolor="rgba(0,0,0,0)",
                             paper_bgcolor="rgba(0,0,0,0)", title_font_color="black", font_color="black")
    line_chart.update_xaxes(showgrid=False)
    # line_chart.update_yaxes(showgrid=False) #

    bar_chart = px.bar(
        df_filterd, x="countriesAndTerritories", y=selected_bar, color="countriesAndTerritories",
        color_discrete_sequence=dark_colors
    )
    bar_chart.update_layout(title=f"{selected_bar}: Bar", template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)", title_font_color="black", font_color="black")

    return (pie_chart, line_chart, bar_chart)


@app.callback(Output('datatable_id', 'selected_rows'),
              [Input('reset-button', 'n_clicks')],
              [State('datatable_id', 'data')])
def reset_selected_rows(n_clicks, data):
    return []


# ------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server()