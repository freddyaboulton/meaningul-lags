import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Forecast Length"),
                dbc.Input(
                    id="forecast-length", placeholder=-1, type="number"
                ),
                dbc.Label("Gap"),
                dbc.Input(
                    id="gap", placeholder=-1, type="number"
                ),
                dbc.Label("Max Delay"),
                dbc.Input(
                    id="max-delay", placeholder=-1, type="number"
                ),
            ]
        ),
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        html.H1("Time Series Window Calculator"),
        html.Hr(),
        html.P("In time series problems, our pipelines need to calculate features based on a 'window' of past features. "
               "The start, end, and size of the window depends on three important time series parameters:"),
        html.Ol([
            html.Li(dcc.Markdown("**Forecast Length**: The number of time steps the model is expected to predict. For now this is equal to the size of the test set.")),
            html.Li(dcc.Markdown("**Gap**: The number of time steps between the training set and the test set.")),
            html.Li(dcc.Markdown("**Max Delay**: The maximum number of timesteps to use for feature engineering, i.e. the window size.")),
        ]),
        html.P(dcc.Markdown("The window is from ranges from **forecast length + gap + max delay** to **gap + forecast length** days before the desired date.")),
        html.Br(),
        dbc.Row([
            dbc.Col(children=controls, width=3),
            dbc.Col(id='window', align="center", width=9),
            ])
    ],
    fluid=True,
)


@app.callback(
    Output('window', 'children'),
    [Input('forecast-length', 'value'),
     Input('gap', 'value'),
     Input('max-delay', 'value')])
def display_dataframes(forecast_length, gap, max_delay):
    input_args = [forecast_length, gap, max_delay]
    if any(value is None for value in input_args):
        return "Please specify non-negative values for Forecast Length, Gap, and Max Delay."
    if any([value < 0 for value in input_args]):
        return "All input values must be non-negative!"
    if forecast_length == 0 or max_delay == 0:
        return "Forecast Length and Max Delay cannot be 0"
    if forecast_length > 5:
        return "Keep the forecast length to <= 5 to be able to visualize in a single page."
    training_dates = pd.date_range("2021-08-01", "2021-08-05", freq="D")
    earliest_features = training_dates - pd.Timedelta(days=max_delay + forecast_length + gap)
    latest_features = training_dates - pd.Timedelta(days=forecast_length + gap)
    training_dates = pd.DataFrame({"Observation Date": training_dates.strftime("%Y-%m-%d"),
                                   f"Earliest Feature Date ({forecast_length + gap + max_delay} days before)": earliest_features.strftime("%Y-%m-%d"),
                                   f"Latest Feature Date ({forecast_length + gap} days before)": latest_features.strftime("%Y-%m-%d"),
                                   })
    training_table = dbc.Table.from_dataframe(training_dates)

    validation_dates = pd.date_range("2021-08-05", periods=forecast_length, freq="D") + pd.Timedelta(days=gap + 1)
    earliest_features = validation_dates - pd.Timedelta(days=max_delay + forecast_length + gap)
    latest_features = validation_dates - pd.Timedelta(days=forecast_length + gap)

    validation_dates = pd.DataFrame({"Observation Date": validation_dates.strftime("%Y-%m-%d"),
                                     f"Earliest Feature Date ({forecast_length + gap + max_delay} days before)": earliest_features.strftime("%Y-%m-%d"),
                                     f"Latest Feature Date ({gap + forecast_length} days before)": latest_features.strftime("%Y-%m-%d"),
                                     })
    validation_table = dbc.Table.from_dataframe(validation_dates)

    return [
            dbc.Row([dbc.Label("Training Data"), training_table]),
            dbc.Row([dbc.Label("Test Data"), validation_table])]


if __name__ == '__main__':
    app.run_server(debug=True)
