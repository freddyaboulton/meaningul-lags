import dash
import dash_bootstrap_components as dbc
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
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(id="window", md=8),
            ],
            align="center",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output('window', 'children'),
    [Input('forecast-length', 'value'),
     Input('gap', 'value'),
     Input('max-delay', 'value')])
def display_hover_data(forecast_length, gap, max_delay):
    input_args = [forecast_length, gap, max_delay]
    if any(value is None for value in input_args):
        return "Please specify non-negative values for Forecast Length, Gap, and Max Delay."
    if any([value < 0 for value in input_args]):
        return "All input values must be non-negative!"
    if forecast_length == 0 or max_delay == 0:
        return "Forecast Length and Max Delay cannot be 0"
    if forecast_length > 5:
        return "Keep the forecast length to <= 5 to be able to visualize in a single page."
    training_dates = pd.date_range("2021-08-01", "2021-08-07", freq="D")
    earliest_features = training_dates - pd.Timedelta(days=max_delay + forecast_length + gap)
    latest_features = training_dates - pd.Timedelta(days=forecast_length + gap)
    training_dates = pd.DataFrame({"Observation Date": training_dates.strftime("%Y-%m-%d"),
                                   "Latest Feature Date": latest_features.strftime("%Y-%m-%d"),
                                   "Earliest Feature Date": earliest_features.strftime("%Y-%m-%d")})
    training_table = dbc.Table.from_dataframe(training_dates)

    validation_dates = pd.date_range("2021-08-07", periods=forecast_length, freq="D") + pd.Timedelta(days=gap + 1)
    earliest_features = validation_dates - pd.Timedelta(days=max_delay + forecast_length + gap)
    latest_features = validation_dates - pd.Timedelta(days=forecast_length + gap)

    validation_dates = pd.DataFrame({"Observation Date": validation_dates.strftime("%Y-%m-%d"),
                                     "Latest Feature Date": latest_features.strftime("%Y-%m-%d"),
                                     "Earliest Feature Date": earliest_features.strftime("%Y-%m-%d")})
    validation_table = dbc.Table.from_dataframe(validation_dates)

    return [dbc.Row([dbc.Label("Training Data"), training_table]), dbc.Row([dbc.Label("Test Data"), validation_table])]


if __name__ == '__main__':
    app.run_server(debug=True)
