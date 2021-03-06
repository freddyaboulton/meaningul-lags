import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.signal import find_peaks
from statsmodels.tsa import stattools

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

MIN_ALPHA = 0.01
MAX_ALPHA = 0.2
STEP = 0.01
slider_marks = {val: {"label": str(round(val, 3)) if i % 2 == 0 else ""} for i, val in enumerate(np.arange(MIN_ALPHA, MAX_ALPHA, step=STEP))}

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Confidence Level"),
                dcc.Slider(id="conf-level", min=MIN_ALPHA,
                           max=MAX_ALPHA, step=STEP, value=0.05,
                           included=False,
                           marks=slider_marks),
                dbc.Label("Dataset"),
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': "SeoulBikeData", 'value': "SeoulBikeData"},
                        {'label': "daily-total-female-births", "value": "daily-total-female-births"},
                        {'label': "southern_oscillation_evenly_spaced", "value": "southern_oscillation_evenly_spaced"},
                        {'label': "monthly_co2", "value": "monthly_co2"},
                        {'label': "monthly-sunspots", "value": "monthly-sunspots"},
                        {'label': "daily_bike_shares", "value": "daily_bike_shares"},
                        {'label': 'AirPassengers', 'value': 'AirPassengers'},
                        {"label": "Alcohol_Sales", "value": "Alcohol_Sales"},
                        {"label": "yahoo_stock", "value": "yahoo_stock"},
                        {"label": "Miles_Traveled", "value": "Miles_Traveled"},
                        {"label": "DailyDelhiClimateTrain", "value": "DailyDelhiClimateTrain"},
                        {"label": "peyton_manning", "value": "peyton_manning"}
                    ],
                    value='SeoulBikeData'
                ),
            ]
        ),
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        html.H1("Meaninful Lags"),
        html.Hr(),
        dbc.Row([
            dbc.Col(children=controls, width=3),
            dbc.Col(dcc.Graph(id="meaningful-lags")),
            ])
        ],
    fluid=True,
)

target_names = {"SeoulBikeData": "Rented Bike Count",
                "daily-total-female-births": "Births",
                "southern_oscillation_evenly_spaced": "oscillation",
                "monthly_co2": "CO2",
                "monthly-sunspots": "Sunspots",
                "daily_bike_shares": "cnt",
                "AirPassengers": "#Passengers",
                "Alcohol_Sales": "S4248SM144NCEN",
                "yahoo_stock": "Adj Close",
                "Miles_Traveled": "TRFVOLUSM227NFWA",
                "DailyDelhiClimateTrain": "meantemp",
                "peyton_manning": "y"}

def plot_significan_lags(y, conf_level, dataset):
    acf_values, ci_intervals = stattools.acf(y, nlags=min(len(y) - 1, 400), fft=True, alpha=conf_level)
    peaks, _ = find_peaks(acf_values)
    index = np.arange(len(acf_values))
    significant = np.logical_or(ci_intervals[:, 0] > 0, ci_intervals[:, 1] < 0)
    first_significant_10 = index[:10][significant[:10]]
    significant_lags = sorted(set(index[significant]).intersection(peaks).union(first_significant_10))
    not_significant_lags = sorted(set(index).difference(significant_lags))
    assert not set(significant_lags).intersection(not_significant_lags)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=significant_lags, 
                              y=acf_values[significant_lags],
                          mode = 'markers',
                          marker_color ='red',
                          marker_size  = 10))
    fig1.add_trace(go.Scatter(x=not_significant_lags, 
                              y=acf_values[not_significant_lags],
                          mode = 'markers',
                          marker_color ='black',
                          opacity=0.2,
                          marker_size  = 10))
    fig1.add_trace(go.Scatter(x=np.arange(len(acf_values)), y=ci_intervals[:, 0] - acf_values,   
                              line_color='blue', opacity=0.1))
    fig1.add_trace(go.Scatter(x=np.arange(len(acf_values)), y=ci_intervals[:, 1] - acf_values,
                              line_color='blue', opacity=0.1, fill='tonexty'))
    fig1.update_yaxes(range=[min(-0.2, min(acf_values), min(ci_intervals[:, 0])) - 0.1, 1.1])
    fig1.update_layout(showlegend=False,
                      title_text=f"{dataset}<br>Statistically significant lags for a {int((1 - conf_level) * 100)}% confidence interval:<br> {significant_lags}")
    return fig1


@app.callback(
    Output('meaningful-lags', 'figure'),
    [Input("dropdown", "value"),
     Input('conf-level', 'value'),
    ])
def display_dataframes(dataset, conf_level):
    ctx = dash.callback_context

    df = pd.read_csv(f"./{dataset}.csv")
    y = df.pop(target_names[dataset])
    return plot_significan_lags(y, conf_level, dataset)


if __name__ == '__main__':
    app.run_server(debug=True)
