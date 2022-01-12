import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import os
import sys

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from app import server


from apps import Surface_sales, Office_sales, xbox_sales


app.layout =html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Surface Products|', href='/apps/Surface_sales'),
        dcc.Link('Office Products|', href='/apps/Office_sales'),
        dcc.Link('Xbox Products', href='/apps/xbox_sales'),
    ], className="row"),
    html.Div(id='page-content')
])
    


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])


def display_page(pathname):
    if pathname == '/apps/Surface_sales':
        return Surface_sales.layout
    if pathname == '/apps/Office_sales':
        return Office_sales.layout
    if pathname == '/apps/xbox_sales':
        return xbox_sales.layout
    else:
        return  "404 Page Error! Please choose a link"
          

# if __name__ == '__main__':
#     app.run_server(debug=False)

if __name__ == "__main__":
    app.run_server(debug=True, port= 8000)



