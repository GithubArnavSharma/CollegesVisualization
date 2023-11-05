import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import plotly.graph_objects as go
import json
import webbrowser
from dash import Dash, dcc, html, Input, Output, ctx, State

df = pd.read_csv("Better_df.csv")

def new_display_list(value):
    if value == 1:
        return [f"{name}<br>{int(100*rate)}%" for name, rate in zip(df["Name"], df["Admission Rate"])]
    elif value == 2:
        return [f"{name}<br>{enroll} " for name, enroll in zip(df["Name"], df["Enrollment"])]
    elif value == 3:
        return [f"{name}<br>{sat}" for name, sat in zip(df[df["SAT75"].notna()]["Name"], df[df["SAT75"].notna()]["SAT75"])]

def new_marker(value, t):
    if value == 1:
        color = list(100*np.array(df["Admission Rate"]))
        if t is not None:
            color = [value if value >= int(t) else "red" for value in color]
            
        return dict(size = 8, opacity = 0.8, reversescale = False, autocolorscale = False, symbol = 'square', line = dict(width=1, color='rgba(102, 102, 102)'),
                    colorscale = 'Blues', cmin = 0, color = color, cmax = 100, colorbar_title="Admission<br>Rate")
    elif value == 2:
        color = df["Enrollment"]
        if t is not None:
            color = [value if value >= int(t) else "red" for value in color]
            
        return dict(size = 8, opacity = 0.8, reversescale = False, autocolorscale = False, symbol = 'square', line = dict(width=1, color='rgba(102, 102, 102)'),
                    colorscale = 'Blues', cmin = 0, color = color, cmax = df["Enrollment"].max(), colorbar_title="Enrollment")
    elif value == 3:
        color = df[df["SAT75"].notna()]["SAT75"]
        if t is not None:
            color = [value if value >= int(t) else "red" for value in color]
            
        return dict(size = 8, opacity = 0.8, reversescale = False, autocolorscale = False, symbol = 'square', line = dict(width=1, color='rgba(102, 102, 102)'),
                    colorscale = 'Blues', cmin = df["SAT75"].min(), color = color, cmax = df["SAT75"].max(), colorbar_title="SAT")

def new_title(value):
    if value == 1:
        return "Admissions Rate for US Colleges"
    elif value == 2:
        return "Enrollment for US Colleges"
    elif value == 3:
        return "75th Percentile SAT for US Colleges"

global college_clicked
college_clicked = ""

geo_dict = dict(scope='usa', projection_type='albers usa', showland = True, landcolor = "rgb(250, 250, 250)", subunitcolor = "rgb(217, 217, 217)",
                countrycolor = "rgb(217, 217, 217)", countrywidth = 0.5, subunitwidth = 0.5)


app = Dash()
app.layout = html.Div([
    html.H1("American Colleges Visualization", style={"text-align": "center", "font-family":"Trebuchet MS", "font-size":40}),

    html.H2("Contributors: Arnav, Araav, Anush", style={"text-align": "center", "font-family":"Trebuchet MS", "font-size":25}),

    html.Br(),

    html.Label(['Map:'], style={'font-weight': 'bold', "text-align": "right", "offset":5, "font-family":"verdana", "font-size":20}),
    
    dcc.Dropdown(id="graph-type",
                 options=[
                     {"label":"Admission Rate", "value":1},
                     {"label":"Enrollment", "value":2},
                     {"label":"75th Percentile SAT", "value":3}],
                 multi=False,
                 value=1,
                 style={"width": "40%", "font-family":"verdana"}
                 ),

    html.Br(),

    html.Label(['Threshold Value:'], style={'font-weight': 'bold', "text-align": "right", "offset":5, "font-family":"verdana", "font-size":20}),

    html.Br(),

    dcc.Input(id='threshold', value = 0, type='number', style={"font-family":"verdana", 'width':'10%', 'font-size':22}),

    html.Br(),

    html.Button(id='threshold-button', children='Submit', style={"font-family":"verdana", 'font-size':17}),

    html.Div(id="output_container", children=[]),
    
    dcc.Graph(id="college-map", figure={}),

    html.Div(id="where")
])

@app.callback(
    [Output(component_id="output_container", component_property="children"),
     Output(component_id="college-map", component_property="figure"),
     Output("where", "children")],
    [Input(component_id="graph-type", component_property="value"),
     Input(component_id="threshold-button", component_property="n_clicks"),
     Input("college-map", "clickData")],
    [State('threshold', 'value')]
    
)

def update_graph(option_slctd, n_clicks, clickData, t):
    global college_clicked
    
    new_df = df.copy()
    if option_slctd == 3:
        new_df = new_df[new_df["SAT75"].notna()]

       
    fig = go.Figure(data=go.Scattergeo(
            locationmode = 'USA-states',
            lon = new_df['Long'],
            lat = new_df['Lat'],
            text = new_display_list(option_slctd),
            mode = 'markers',
            marker = new_marker(option_slctd, t)
    ))

    the_college = ""
    if clickData:
        lon = clickData["points"][0]["lon"]
        lat = clickData["points"][0]["lat"]
        
        potential_colleges = df[(df["Long"] == lon) & (df["Lat"] == lat)]
        if potential_colleges.shape[0] > 0:
            the_college = potential_colleges["Name"].iloc[0]
            
            if college_clicked != the_college:
                college_clicked = the_college
                the_college = the_college.replace(" ", "_")
                webbrowser.open_new_tab(f"https://en.wikipedia.org/wiki/{the_college}")


    fig.update_layout(
            title = new_title(option_slctd),
            geo = geo_dict,
            width=1450,
            height=700
    )

    
    return "", fig, ""
    
app.run_server(debug=True, use_reloader=False)
