# Import web scraping
import subprocess
import json
import requests
from zipfile import ZipFile
# Import Data packages
import pandas as pd
import numpy as np
# Import Dash packages
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
# Import Plotly packages
import plotly.express as px

# DATA READING
# -------------------------------------------------------------------------------------------------

# Download dataset as zip
print('Beggining download of kaggle dataset')
subprocess.call('kaggle datasets download sudalairajkumar/novel-corona-virus-2019-dataset')

# Name of zip folder and file to extact
zip_name = 'novel-corona-virus-2019-dataset.zip'
file_name = 'covid_19_data.csv'

# opening the zip file in READ mode
with ZipFile(zip_name, 'r') as zip:
    # printing all the contents of the zip file
    zip.printdir()
    print('Extacting {file_name}...')
    zip.extract(file_name)
    print('Done!')

# Read Data
all_data = pd.read_csv(file_name)

# -------------------------------------------------------------------------------------------------

# DATA CLEANING
# -------------------------------------------------------------------------------------------------

# Aggregate Data - group by country
clean_df = all_data.groupby(
    ['ObservationDate', 'Country/Region'], as_index=False)[['Confirmed', 'Deaths', 'Recovered']].sum()

# Remove countries that start with a bracket or white space.
clean_df = clean_df[~((clean_df['Country/Region'].str.match('^\('))
                      | (clean_df['Country/Region'].str.match('^\s')))]

# Rename countries to match geojson names
clean_df = clean_df.replace(
    {'US': 'United States of America', 'UK': 'United Kingdom', 'Mainland China': 'China'})

# Rename the columns
clean_df.rename(columns={'ObservationDate': 'Date',
                         'Country/Region': 'Country'}, inplace=True)

# -------------------------------------------------------------------------------------------------

# EDA
# -------------------------------------------------------------------------------------------------

# Statistics
# ------------------------------------------------

# Get date of most recent update
date = clean_df.iloc[-1]['Date']

# Get number of days
num_days = len(clean_df.Date.unique())

# Get stats
total_confirmed = clean_df[clean_df['Date'] == date]['Confirmed'].sum()
total_deaths = clean_df[clean_df['Date'] == date]['Deaths'].sum()
total_recovered = clean_df[clean_df['Date'] == date]['Recovered'].sum()

# Get list of unique countries
countries_list = clean_df['Country'].unique()
# Sort list in alphabetical order
countries_list.sort()

# ------------------------------------------------

# INTERACTIVE MAP
# ------------------------------------------------

# Calcualate the interval (to get about 10 values)
interval = round(len(clean_df['Date'].unique())/10)

# Create list of about 11 dates (10 with a gap of size interval and 1 being the final date)
plot_dates = np.append(clean_df['Date'].unique()[
                       :-2:interval], clean_df['Date'].unique()[-1])

# Create dataframe of interval dates
intervals = clean_df[(clean_df['Date'].isin(plot_dates))
                     & (clean_df['Deaths'] > 1)]

# Request geojson
response = requests.get(
    'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')

# Parse geojson file text as json
countries = json.loads(response.text)

# Get mapbox acces token
mapbox_access_token = 'pk.eyJ1IjoiZGF2aWRudzE5OTgiLCJhIjoiY2s4b2drbGtoMDRpeTNncWk4eTdkZWNkNSJ9._yhEzCDPO1jUbq6ATqZspQ'

# Plot figure
map_fig = px.choropleth_mapbox(intervals, geojson=countries, color="Deaths",
                               locations="Country",
                               featureidkey='properties.name',
                               center={"lat": 25, "lon": 0},
                               zoom=1,
                               animation_frame='Date',
                               animation_group='Deaths',
                               range_color=[1, max(intervals['Deaths'])],
                               height=600)

# Change theme to dark
map_fig.layout.template = 'plotly_dark'

map_fig.update_layout(
    mapbox_accesstoken=mapbox_access_token,
    margin={"r": 0, "t": 0, "l": 0, "b": 0})


# ------------------------------------------------

# LINE PLOT DROP DOWN
# -------------------------------------------------

# Create list of country dictionaries for dropdown
dropdown_countries = [{'label': c, 'value': c} for c in countries_list]

# -------------------------------------------------

# TABLE
# -------------------------------------------------

# Get only the records for the most recent date
newest_data = clean_df[clean_df['Date'] ==
                       date].drop('Date', axis=1).reset_index(drop=True)

# Regular HTML/Bootstap table
table = dbc.Table.from_dataframe(
    newest_data, className='table-hover', id='main-table')

# -------------------------------------------------------------------------------------------------

# CREATE APP
# -------------------------------------------------------------------------------------------------

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# App layout
app.layout = html.Div([
    html.H1('COVID-19 DASHBOARD', className='text-center mt-5'),

    html.Div('''
        A dashboard showing Covid-19 data.
    ''', className='text-center'),
    html.Div([
        # Row 1
        html.Div([
            # Col 1
            html.Div([
                # Stats
                html.Div([
                    html.H4('COVID-19 STATS'),
                    html.Hr(),
                    html.P(f'{int(total_confirmed):,d}', id='cases'),
                    html.P('Total Confirmed Cases'),
                    html.Hr(),
                    html.P(f'{int(total_deaths):,d}', id='dead'),
                    html.P('Total Dead'),
                    html.Hr(),
                    html.P(f'{int(total_recovered):,d}', id='recovered'),
                    html.P('Total Recovered')],
                    className='card',
                    id='facts1'
                ),
                # Last Updated
                html.Div([
                    html.P('Last Updated (MM/DD/YYYY)'),
                    html.H3(date)],
                    className='card',
                    id='update-date'
                )],
                className='column-container',
                id='column1'
            ),
            # Col 2 (Map)
            html.Div([
                html.H4('Deaths per Country'),
                dcc.Graph(figure=map_fig)],
                className='card',
                id='map1'
            )],
            className='row-container'
        ),
        # Row 2
        html.Div([
            # Col 1
            html.Div([
                # Title
                html.H4('Deaths over Time'),
                # Dropdown Country MultiSelect
                dcc.Dropdown(
                    options=dropdown_countries,
                    value=['United States of America', 'China'],
                    multi=True,
                    placeholder='Select Countries...',
                    id='country-select-dd'
                ),
                # Name of the country
                dcc.Graph(id='line-graph-deaths')],
                className='card',
                id='line-dot'
            ),
            # Col 2
            # html.Div([
            #     html.H4('Empty Card'),
            # ],
            #     className='card',
            #     id='country-select'
            # )
            ],
            className='row-container'
        ),
        # Row 3
        html.Div([
            # Title
            html.H4('World Cases'),
            # Table
            html.Div([
                table],
                className='data-table',
                id='data-table'
            )],
            className='card'
        )],
        className='column-container'
    )
])

# CALLBACKS
# -------------------------------------------------------------------------------------------------

# Line Plot Countries
# ------------------------------------------------


@app.callback(
    Output('line-graph-deaths', 'figure'),
    [Input('country-select-dd', 'value')]
)
def update_line_plot(selected_countries):

    if len(selected_countries) == 0:
        raise Exception('No countries specified!')

    # Get specific country cases
    country_cases = clean_df.loc[clean_df['Country'].isin(selected_countries)].replace(
        {'United States of America': 'US', 'United Kingdom': 'UK'})

    # Create line graph on country cases
    line_fig = px.line(country_cases, x='Date', y='Deaths', color='Country', range_x=[
                       '01/22/2020', '04/30/2020'], height=600)

    # Create line graph on country cases
    line_fig = px.line(country_cases, x='Date',
                       y='Deaths', color='Country', range_x=['01/22/2020', '04/30/2020'], height=600)

    line_fig.update_xaxes(rangeslider_visible=True)

    # Change x axis
    line_fig.update_layout(
        xaxis=dict(
            tickvals=plot_dates
            # ticktext = intervals
        )
    )

    # Change theme to dark
    line_fig.layout.template = 'plotly_dark'

    return line_fig

# ------------------------------------------------

# -------------------------------------------------------------------------------------------------

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
