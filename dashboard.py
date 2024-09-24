# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Define dropdown options for launch sites
options = [
    {'label': 'All Sites', 'value': 'All'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for launch site selection
    dcc.Dropdown(id='site-dropdown',
                 options=options,
                 value='All',
                 placeholder='Select a Launch Site here',
                 searchable=True
    ),
    html.Br(),

    # Pie chart for launch success distribution
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Slider for payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: "0", 10000: '10000'},
                    value=[min_payload, max_payload]),

    # Scatter chart for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df

    if entered_site == 'All':
        # Show overall success distribution
        values = filtered_df['class'].value_counts()
        fig = px.pie(
            names=values.index,
            values=values.values,
            title='Launch Success Distribution for All Sites'
        )
    else:
        # Filter data for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        if filtered_df.empty:
            # Handle the case where there are no launches for the selected site
            fig = px.pie(values=[0], names=['No Data'], title=f'No Data for {entered_site}')
        else:
            values = filtered_df['class'].value_counts()
            fig = px.pie(
                names=values.index,
                values=values.values,
                title=f'Launch Success Distribution for {entered_site}'
            )
    
    return fig
# Callback for the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter(entered_site, payload_range):
    filtered_df = spacex_df
    # Filter by selected payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site == 'All':
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y='class',
                         color="Booster Version Category",
                         title='Payload Mass vs Launch Success for All Sites')
    else:
        # Filter for the selected launch site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y='class',
                         color="Booster Version Category",
                         title=f'Payload Mass vs Launch Success for {entered_site}')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8054)
