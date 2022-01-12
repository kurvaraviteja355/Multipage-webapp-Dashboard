import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import os
import sys
import pathlib

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

predicted_data = pd.read_csv(DATA_PATH.joinpath("Xbox_predictions2.csv"))

#predicted_data = pd.read_csv('Predicted_data/Xbox_predictions2.csv')

predicted_data["ds"] = pd.to_datetime(predicted_data["ds"])

predicted_data = predicted_data.dropna()

def column_value(df_product, column):
    
    df_product['decimal'] = df_product[column]%1
    df_product['decimal2'] = df_product[column]//1
    df_product['decimal2'] = df_product['decimal2'].astype(int)
    df_product['decimal'] = (df_product['decimal'] > 0.8).astype(int)
    df_product[column] = df_product['decimal']+df_product['decimal2']
    df_product = df_product.drop(['decimal', 'decimal2'], 1)
    
    return df_product

#predicted_data = column_value(predicted_data, 'yhat')
predicted_data = column_value(predicted_data, 'yhat_upper')
predicted_data = column_value(predicted_data, 'yhat_lower')

predicted_data = round(predicted_data)

data = predicted_data.loc[predicted_data['ds'] >= '2021-10-01']
data = data.dropna()

fig = go.Figure(
        data = [
            go.Bar(
                name = 'real values',
                x = data['Business_Unit'],
                y =  data['y'],
                base = 'relative',
                offsetgroup = 0,
            ),
            go.Bar(
                name = 'predicted values',
                x = data['Business_Unit'],
                y =  data['yhat'],
                base = 'relative',
                offsetgroup = 1,
            ),
            go.Bar(
                name = 'predicted upper_limit',
                x = data['Business_Unit'],
                y =  data['yhat_upper'],
                base = 'relative',
                offsetgroup = 2,
            ),
        ],
        layout=go.Layout(
            title = {'text' : 'Xbox Console prediction for next two weeks', 
            'y' : 0.9, 'x' : 0.5, 'xanchor' : 'center', 'yanchor':'top'},
            yaxis_title = 'Sales',
            width=None,
            height=500,
        )
    )

def onLoad_cities_options():
    '''Actions to perform upon initial page load'''

    city_options = (
        [{'label': city, 'value': city}
         for city in data['Reseller_City'].unique()]
    )
    return city_options




# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN],
# meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale =1.0" }]
# )


###### Layout section : Bootstrap
#----------------------------------------------------------------------------------------
layout =  html.Div(dbc.Container([

    dbc.Row([
        dbc.Col(html.H1('Microsoft Xbox products prediction Dashborad', className = 'text-center text-primary'),
        
                width = 12)
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id = 'xbox_graph_country', figure = fig, style={'float': 'right','margin': 'auto'})
            ], width = {'size' : 5}),


        dbc.Col([
            dcc.Dropdown(id = 'xbox_City_dropdown', multi=False, value ='Berlin',
            options = [{'label': i, 'value': i} for i in data['Reseller_City'].unique()]),
            dcc.Graph(id = 'xbox_bar_garph_city', figure={ }, style={'float': 'right','margin': 'auto'})

        ], width = {'size' : 5})
       

        
    ], className="g-1", justify='around'),


     dbc.Row([

        dbc.Col([
            dcc.Dropdown(id='xbox_City_selector', multi=False, options= onLoad_cities_options()),
            dcc.Dropdown(id='xbox_product_selector',  multi=False),
            dcc.Graph(id = 'xbox_Results_table', figure={}),
            dcc.Graph(id = 'xbox_Graph_plot_sales', figure = {})
            ], width = {'size' : 11}),
        ], className="g-1", justify='around')

], fluid=True))



##### Bar chart for city-wise prediction ------------------------------------------------

@app.callback(
    [Output(component_id='xbox_bar_garph_city', component_property='figure'),
    Output(component_id = 'xbox_product_selector', component_property='options'),
    Output(component_id = 'xbox_Results_table', component_property='figure'),
    Output(component_id = 'xbox_Graph_plot_sales', component_property= 'figure'),],
    [Input(component_id='xbox_City_dropdown', component_property='value'),
    Input(component_id = 'xbox_City_selector', component_property='value'),
    Input(component_id = 'xbox_City_selector', component_property= 'value'),
    Input(component_id = 'xbox_product_selector', component_property= 'value')]

)

def update_graph(selected_city, city, Area, item):

    city_data = data[data["ds"] >= '2021-10-01']
    city_data = data[data["Reseller_City"] == selected_city]
    
    line_fig = go.Figure(data = [
         go.Bar(
                name = 'Real values',
                x = city_data['Business_Unit'],
                y = city_data['y'],
                base = 'relative',
                offsetgroup = 0,
                ),
        go.Bar(
            name = 'predicted values',
            x = city_data['Business_Unit'],
            y = city_data['yhat'],
            base = 'relative',
            offsetgroup = 1,
            ),
        go.Bar(name = 'predicted upper_limit',
                x = city_data['Business_Unit'],
                y =  city_data['yhat_upper'],
                base = 'relative',
                offsetgroup = 2,
                ),
        ],
        layout=go.Layout(
            title = {'text' : 'Surface devices city-wise predictions', 
            'y' : 0.9, 'x' : 0.5, 'xanchor' : 'center', 'yanchor':'top'},
            yaxis_title = 'Sales',
        )
    )
    ############################## Load products in dropdown ####################################
    products_df = data.loc[data['Reseller_City'] == city]

    product = [{'label' : product, 'value': product} for product in products_df['Business_Unit'].unique()]




    ############################Load the table with selected dropdown ###############################
    results = data.loc[(data['Reseller_City'] == Area) & (data['Business_Unit'] == item)]

    cols = ["ds", 'Business_Unit', "y", "yhat", "yhat_upper", 'training_date']

    fig_table = go.Figure(data=[go.Table(
        columnwidth = [5,5, 5, 5, 5, 5],
        header=dict(values=list(results[cols]), fill_color ="paleturquoise", align ="left"),

        cells = dict(values = [results["ds"], results['Business_Unit'], results["y"], results["yhat"], results["yhat_upper"], results['training_date']], fill_color="lavender", align='left'))
    ])


    ################################# Load the graph with selected dropdown   ############################

    graph_data = predicted_data.loc[(predicted_data['Reseller_City'] == Area) & (predicted_data['Business_Unit'] == item)]




    figure  = go.Figure(data = [
        go.Scatter(x=graph_data['ds'], y=graph_data['y'], name='Actual'),
        go.Scatter(x=graph_data['ds'], y=graph_data['yhat'], name='Predicted'),
        go.Scatter(x=graph_data['ds'], y=graph_data['yhat_upper'], name='predicted_upper_limit'),
    ], layout= go.Layout(
        title = 'Actual and predcited graph',
        yaxis_title = 'Sales',
        showlegend=False

    )
    )


    return line_fig, product, fig_table, figure


# if __name__ == "__main__":
#     app.run_server(debug=True, port= 3000)


      

