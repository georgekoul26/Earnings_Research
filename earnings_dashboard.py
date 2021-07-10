#import libraries
import yfinance as yf
import hvplot.pandas
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc 
import dash_html_components as html


#Import Price data
data_path = Path('price_history.csv')
price_hx = pd.read_csv(data_path, header=[0,1], index_col=[0], parse_dates=True, infer_datetime_format=True)
price_hx = price_hx['2019-07-07':]

#Slice out close prices and calculate returns
returns_df = price_hx.xs('close', level=1, axis=1).pct_change()
returns_df.dropna(inplace=True)
cum_returns = ((1+returns_df).cumprod()-1)* 100

data_path = Path('JPM_earnings.csv')
jpm_earnings = pd.read_csv(data_path, index_col=[0], parse_dates=True, infer_datetime_format=True)


#Caluculate Rolling covarience and varience
returns_df['COV'] = returns_df['JPM'].rolling(window=10).cov(returns_df['SPY'])
returns_df['VAR'] = returns_df['JPM'].rolling(window=10).var()
returns_df['BETA'] = returns_df['COV']/returns_df['VAR']
returns_df['BETA'].hvplot(title= '10 Day Rolling Beta') + price_hx['JPM']['close'].hvplot()

beta_fig = px.line(returns_df, x=returns_df.index, y=returns_df['BETA'], labels={'index' : 'Date'})

#Create function to format figures with earnings bands
def format_fig(figure, remove_weekends=True):
    figure.add_vrect(
        x0='2019-07-16', x1='2019-07-30',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2019-10-15', x1='2019-10-29',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2020-01-14', x1='2020-01-28',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2020-04-14', x1='2020-04-28',
        fillcolor='red', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2020-07-14', x1='2020-07-28',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2020-10-13', x1='2020-10-27',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2021-01-15', x1='2021-02-01',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.add_vrect(
        x0='2021-04-14', x1='2021-04-28',
        fillcolor='green', opacity=.2,
        layer='below', line_width=0,
    )
    figure.update_xaxes(rangeslider_visible=True)
    figure.update_yaxes(fixedrange=False)
    if remove_weekends == True:
        figure.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]), #hide weekends
                dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
            ]
        )
#Create beta fig
format_fig(beta_fig)

#Create hx fig
hx_fig = go.Figure(data=[go.Candlestick(x=price_hx.index,
                        open=price_hx['JPM']['open'],
                        high=price_hx['JPM']['high'],
                        low=price_hx['JPM']['low'],
                        close=price_hx['JPM']['close'],)])
format_fig(hx_fig)

#create price hx fig
price_fig = px.line(cum_returns, x=cum_returns.index, y=[cum_returns['JPM'], cum_returns['SPY']], labels={'index' : 'Date'})
format_fig(price_fig, remove_weekends=False)

#Create earnings fig
colors = ['green',] *8
colors[3] = 'red'

earnings_fig = go.Figure(data=[
    go.Bar(y=jpm_earnings['Consensus Estimate'],x=jpm_earnings.index, name='Consensus Estimate', marker_color='lightslategray'),
    go.Bar(y=jpm_earnings['Actual EPS'], x=jpm_earnings.index, name='Acutal EPS', marker_color=colors)])
earnings_fig.update_layout(barmode='group', xaxis_tickangle=-45, yaxis_title='EPS',xaxis_tickmode='array', xaxis_tickvals=jpm_earnings.index)

#slice out close prices
close=price_hx.xs('close', level=1, axis=1)
#Create sliced df for fig2
sliced_df = pd.DataFrame({
    '2019-07-16' : close.loc['2019-07-08':'2019-07-30','JPM'],
    '2019-10-15' : close.loc['2019-10-07':'2019-10-29','JPM'],
    '2020-01-14' : close.loc['2020-01-06':'2020-01-28','JPM'],
    '2020-04-14' : close.loc['2020-04-06':'2020-04-28','JPM'],
    '2020-07-14' : close.loc['2020-07-06':'2020-07-28','JPM'],
    '2020-10-13' : close.loc['2020-10-05':'2020-10-27','JPM'],
    '2021-01-15' : close.loc['2021-01-07':'2021-02-01','JPM'],
    '2021-04-14' : close.loc['2021-04-06':'2021-04-28','JPM'],
})
sliced_df.reset_index(inplace=True)
sliced_df = sliced_df.apply(lambda x: pd.Series(x.dropna().values))
sliced_df.dropna(inplace=True)
sliced_df.drop(columns='index', inplace=True)
sliced_ret = sliced_df.pct_change()
sliced_cum = ((1+sliced_ret).cumprod()-1)* 100
sliced_cum.dropna(inplace=True)
sliced_cum.reset_index(drop=True, inplace=True)

#Create alternate sliced df for fig1 
sliced_df1 = pd.DataFrame({
    '2019-07-16' : close.loc['2019-07-16':'2019-07-30','JPM'],
    '2019-10-15' : close.loc['2019-10-15':'2019-10-29','JPM'],
    '2020-01-14' : close.loc['2020-01-14':'2020-01-28','JPM'],
    '2020-04-14' : close.loc['2020-04-14':'2020-04-28','JPM'],
    '2020-07-14' : close.loc['2020-07-14':'2020-07-28','JPM'],
    '2020-10-13' : close.loc['2020-10-13':'2020-10-27','JPM'],
    '2021-01-15' : close.loc['2021-01-15':'2021-02-01','JPM'],
    '2021-04-14' : close.loc['2021-04-14':'2021-04-28','JPM'],
})
sliced_df1.reset_index(inplace=True)
sliced_df1 = sliced_df1.apply(lambda x: pd.Series(x.dropna().values))
sliced_df1.dropna(inplace=True)
sliced_df1.drop(columns='index', inplace=True)
sliced_ret1 = sliced_df1.pct_change()
sliced_cum1 = ((1+sliced_ret1).cumprod()-1)* 100
sliced_cum1.fillna(0, inplace=True)
sliced_cum1.reset_index(drop=True, inplace=True)
sliced_cum1

#Create fig1 - cumulative returns
ret_fig1 = go.Figure()
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2019-07-16'], mode='lines', name='2019-07-16', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2019-10-15'], mode='lines', name='2019-10-15', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2020-01-14'], mode='lines', name='2020-10-14', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2020-04-14'], mode='lines', name='2020-04-14', line=dict(color='red', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2020-07-14'], mode='lines', name='2020-07-14', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2020-10-13'], mode='lines', name='2020-10-13', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2021-01-15'], mode='lines', name='2021-01-15', line=dict(color='green', width=2)))
ret_fig1.add_trace(go.Scatter(x=sliced_cum1.index, y=sliced_cum1['2021-04-14'], mode='lines', name='2021-04-14', line=dict(color='green', width=2)))
ret_fig1.update_layout(title='Cumulative Returns Following Earnings Report',
                     xaxis_title='Number of Trading Days',
                     yaxis_title='Cumulative Return')
ret_fig1.add_hline(y='0')


#Create fig2 
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2019-07-16'], mode='lines', name='2019-07-16', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2019-10-15'], mode='lines', name='2019-10-15', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2020-01-14'], mode='lines', name='2020-10-14', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2020-04-14'], mode='lines', name='2020-04-14', line=dict(color='red', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2020-07-14'], mode='lines', name='2020-07-14', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2020-10-13'], mode='lines', name='2020-10-13', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2021-01-15'], mode='lines', name='2021-01-15', line=dict(color='green', width=2)))
fig2.add_trace(go.Scatter(x=sliced_cum.index, y=sliced_cum['2021-04-14'], mode='lines', name='2021-04-14', line=dict(color='green', width=2)))
fig2.update_layout(title='Cumulative Returns Following Earnings Report',
                     xaxis_title='Number of Trading Days',
                     yaxis_title='Cumulative Return')
fig2.add_hline(y='0')
fig2.add_vrect(
    x0=0, x1=4,
    fillcolor='gray', opacity=.4,
    layer='below', line_width=0,
)


#Dash test area

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Earnings Research'),

    dcc.Graph(
        id='Candlestick',
        figure=hx_fig),
    dcc.Graph(
        id='Returns',
        figure=price_fig),
    dcc.Graph(
        id='Beta',
        figure=beta_fig),
    dcc.Graph(
        id='Earnings',
        figure=earnings_fig),
    dcc.Graph(
        id='Returns Post',
        figure=ret_fig1),
    dcc.Graph(
        id='Returns PRE/Post',
        figure=fig2),
    

])

if __name__ == '__main__':
    app.run_server(debug=True)
