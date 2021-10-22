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

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Confidence Level"),
                dcc.Slider(id="conf-level", min=0.01,
                           max=0.10, step=0.01, value=0.05),
                dbc.Label("Dataset"),
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': "SeoulBikeData", 'value': "SeoulBikeData"},
                        {'label': "daily-total-female-births", "value": "daily-total-female-births"},
                        {'label': "southern_oscillation_evenly_spaced", "value": "southern_oscillation_evenly_spaced"},
                        {'label': "monthly_co2", "value": "monthly_co2"},
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
                "monthly_co2": "CO2"}

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
                          opacity=0.1,
                          marker_size  = 10))
    fig1.update_layout(showlegend=False,
                      title_text=f"{dataset}<br>Statistically significant lags:<br> {significant_lags}")
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
