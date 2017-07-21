import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import quickstart
import pandas as pd
from datetime import datetime

app = dash.Dash()
data = quickstart.getData()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
prettyDf = df.sort_values('Date', ascending=False)
df['Start Time'] = pd.to_datetime(df['Start Time'], format='%I:%M:%S %p')
df['End Time'] = pd.to_datetime(df['End Time'], format='%I:%M:%S %p')
df['Elapsed Time'] = pd.to_numeric(df['Elapsed Time'])
df['Week Num'] = df['Date'].dt.week
df['Week Day'] = df['Date'].dt.dayofweek
df['Week Day Name'] = df['Date'].dt.weekday_name
myBins = [datetime.strptime('12:00:00 AM', '%I:%M:%S %p'),
          datetime.strptime('04:00:00 AM', '%I:%M:%S %p'),
          datetime.strptime('08:00:00 AM', '%I:%M:%S %p'),
          datetime.strptime('12:00:00 PM', '%I:%M:%S %p'),
          datetime.strptime('04:00:00 PM', '%I:%M:%S %p'),
          datetime.strptime('08:00:00 PM', '%I:%M:%S %p'),
          datetime.strptime('11:59:59 PM', '%I:%M:%S %p')]
myLabels = ['Middle of Night', 'Early Morning',
            'Morning', 'Afternoon', 'Evening', 'Late Night']
df['Time of Day'] = pd.cut(df['Start Time'], bins=myBins, labels=myLabels)
print(df.groupby(['Time of Day']).count())


def generate_table(dataframe, max_rows=10, styles={'minmax': '250px 50%', 'justifyContent': 'center'}):
    # columns = []
    # if isinstance(dataframe, pd.DataFrame):
    # else:
    return html.Table(
        # Header
        [html.Tr([html.Th(col, style={'textAlign': 'center',  'padding': '12px 15px', 'borderBottom': '1px solid #E1E1E1'}) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(children=dataframe.iloc[i][col], style={'textAlign': 'center',  'padding': '12px 15px', 'borderBottom': '1px solid #E1E1E1'}) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))], style={'minMax': '300px 50%'}
    )


graphTypes = ['Daily Summary', 'Weekly Summary',
              'Project Summary', 'Time of Day Analysis']
app.layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(
            id='graphType',
            options=[{'label': i, 'value': i} for i in graphTypes],
            value='Daily Summary'
        )], style={'width': '300px', 'display': 'inline-block'}),
    html.H1(id='title', style={'textAlign': 'center', 'color': '#7FDFF'}),
    dcc.Graph(id='graphic'),
    html.Div(style={'display': 'flex', 'flexFlow': 'row wrap', 'justifyContent': 'center'},
             children=[generate_table(prettyDf),
                       html.Div(id='summary', style={'display': 'flex', 'flexFlow': 'row wrap', 'justifyContent': 'flex-end'})]
             )

])


@app.callback(
    Output(component_id='graphic', component_property='figure'),
    [Input(component_id='graphType', component_property='value')]
)
def updateGraph(topic):
    if topic == 'Daily Summary':
        return {
            'data': [go.Scatter(
                x=df.groupby('Date').apply(lambda x: x.name),
                y=df.groupby('Date')['Elapsed Time'].sum(),
                text='Total Daily Hours',
                mode='lines+markers',
                marker={
                    'size': 15,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'blue'}
                }
            )],
            'layout': go.Layout(

                xaxis={
                    'title': 'Date',

                },
                yaxis={
                    'title': 'Session Length',
                },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                hovermode='closest'
            )
        }
    elif topic == 'Weekly Summary':
        return {
            'data': [go.Scatter(
                x=df.groupby('Week Num').first()['Date'],
                y=df.groupby('Week Num')['Elapsed Time'].sum(),
                text='Total Daily Hours',
                mode='lines+markers',
                marker={
                    'size': 15,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'blue'}
                }
            )],
            'layout': go.Layout(

                xaxis={
                    'title': 'Date of Week',

                },
                yaxis={
                    'title': 'Weekly Hours',
                },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                hovermode='closest'
            )
        }
    elif topic == 'Project Summary':
        return {
            'data': [go.Bar(
                x=df.groupby('Topic').apply(lambda x: x.name),
                y=df.groupby('Topic')['Elapsed Time'].sum(),
                text='Total Project Hours'
            )],
            'layout': go.Layout(

                xaxis={
                    'title': 'Project',

                },
                yaxis={
                    'title': 'Total Time Spent',
                },
                margin={'l': 40, 'b': 100, 't': 10, 'r': 0},
                hovermode='closest'
            )
        }
    elif topic == 'Time of Day Analysis':
        return {
            'data': [go.Bar(
                y=df.groupby(['Time of Day']).count()['Date'],
                x=df.groupby('Time of Day').apply(lambda x: x.name),
            )],
            'layout': go.Layout(

                xaxis={
                    'title': 'Time of Day',

                },
                yaxis={
                    'title': 'Number of Sessions Started',
                },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                hovermode='closest'
            )
        }


@app.callback(

    Output('title', 'children'),
    [Input(component_id='graphType', component_property='value')]
)
def updateTitle(topic):
    if topic == 'Daily Summary':
        return 'Daily Average: {0:.2f}'.format(df.groupby('Date')['Elapsed Time'].sum().mean())
    elif topic == 'Weekly Summary':
        return 'Weekly Average: {0:.2f}'.format(df.groupby('Week Num')['Elapsed Time'].sum().mean())
    elif topic == 'Project Summary':
        return 'Average Project Hours: {0:.2f} \n Total Projects: {1}'.format(df.groupby('Topic')['Elapsed Time'].sum().mean(), len(df.groupby('Topic')))


@app.callback(

    Output('summary', 'children'),
    [Input(component_id='graphType', component_property='value')]
)
def updateSummary(topic):
    if topic == 'Daily Summary':
        sumSeries = df['Elapsed Time'].describe()
        sumDf = pd.DataFrame(
            {'Session Stat': sumSeries.index, 'Value': sumSeries.values})
        return generate_table(sumDf, styles={'minmax': '250px 50%', 'justifyContent': 'right'})


if __name__ == '__main__':
    app.run_server()
