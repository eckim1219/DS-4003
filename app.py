# %%
# Import dependencies
import sys
print(sys.executable)

import pandas as pd
import numpy as np
import dash
import base64
import io
from io import BytesIO
import plotly.express as px
import seaborn as sns
from dash import Dash, dcc, html, Input, Output
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# %%
# Import the data
data = pd.read_csv("cleandata")

# Defining the genre color map, used to color each genre by a specific color for the wordcloud
genre_color_map = {
    'neo mellow': 'PaleVioletRed',
    'detroit hip hop': 'DarkOrange',
    'dance pop': 'LightGreen',
    'pop': 'MediumPurple',
    'canadian pop': 'LightSkyBlue',
    'barbadian pop': 'Gold',
    'atl hip hop': 'FireBrick',
    'australian pop': 'MediumOrchid',
    'indie pop': 'LimeGreen',
    'art pop': 'Aqua',
    'colombian pop': 'Coral',
    'big room': 'RoyalBlue',
    'british soul': 'DarkSlateGray',
    'chicago rap': 'DarkRed',
    'acoustic pop': 'SandyBrown',
    'permanent wave': 'DarkCyan',
    'boy band': 'DarkViolet',
    'baroque pop': 'MediumTurquoise',
    'celtic rock': 'Sienna',
    'electro': 'BlueViolet',
    'complextro': 'Orchid',
    'canadian hip hop': 'Tomato',
    'candy pop': 'HotPink',
    'alaska indie': 'DarkMagenta',
    'folk-pop': 'DarkGoldenRod',
    'metropopolis': 'MediumSeaGreen',
    'house': 'Navy',
    'australian hip hop': 'Lime',
    'electropop': 'Orchid',
    'australian dance': 'MediumSpringGreen',
    'hollywood': 'Gold',
    'canadian contemporary r&b': 'Chocolate',
    'irish singer-songwriter': 'DarkOliveGreen',
    'tropical house': 'DarkKhaki',
    'belgian edm': 'DarkOrchid',
    'french indie pop': 'Teal',
    'hip hop': 'Red',
    'danish pop': 'DeepPink',
    'latin': 'DarkSalmon',
    'canadian latin': 'Peru',
    'electronic trap': 'SteelBlue',
    'edm': 'Indigo',
    'electro house': 'MediumBlue',
    'downtempo': 'Olive',
    'brostep': 'Purple',
    'contemporary country': 'DarkSlateBlue',
    'moroccan pop': 'MediumVioletRed',
    'escape room': 'SlateBlue',
    'alternative r&b': '#003F5C'
}

# Creating available columns for dropdown
available_columns = [col for col in data.columns if col not in ['title', 'artist', 'top genre', 'year']]

# Defining options for the dropdown wordcloud genre
dropdown_options = [{'label': genre, 'value': genre} for genre in data['top genre'].unique()]

# Initialize app with stylesheet
external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootswatch/3.3.7/cerulean/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Define app layout
app.layout = html.Div([
    #html.H1("Top Songs Analysis", style={'margin-bottom': '20px'}),  # title
    html.H1("Top Songs Analysis", style={'margin-bottom': '30px', 'margin-top': '30px', 'text-align': 'center'}),  # title
    html.P("This dataset used for this project shows a comprehensive summary of the music industry, presenting the top 10 songs from 2010 to 2019 globally. Collected from Spotify and Billboard, it shows current music trends in various areas and among various groups of people. Spotify is one of the biggest and popular applications people use for music streaming as both artists and producers release their singles, albums, and exclusive content through this platform. With a wide collection of data encompassing consumer preferences and listening habits, Spotify gives a valuable resource for understanding what drives viral hits in the music industry. The goal of this project is to take the insights from this dataset and create an interactive dashboard that will allow users to dive into different genres, styles, and the overall most popular songs throughout the world. This would provide personalized music recommendations based on the user preferences and give the opportunity for users to explore new songs. Although there were many other datasets available, this dataset specifically stood out because of its balance of depth and breadth of information which provides a solid basis for accomplishing my goal of this project. Thank you for taking the time to look through my dashboard!", style={'margin-bottom': '30px'}),  # Your description here

    # Layout for year slider
    html.Div([
        html.Div([
            dcc.RangeSlider(
                id='year-slider',
                min=data['year'].min(), # min value 2010
                max=data['year'].max(), # max value 2019
                step=1,
                value=[data['year'].min(), data['year'].max()], # default value has years 2010 - 2019 selected
                marks={year: str(year) for year in range(data['year'].min(), data['year'].max() + 1, 1)},
            )
        ])
    ], style={'margin-bottom': '30px'}),

    # Container for word cloud and heatmap
    html.Div([
        # Sub-container for word cloud
        html.Div([
            html.Div([
                html.H3("Top Artist Visualization"), # title for wordcloud
                html.Div(id='wordcloud-container', style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-bottom': '20px', 'margin-top': '20px'}), # take up 50% of the left side of the screen
            ], style={'width': '50%', 'display': 'inline-block'}),  # style to make it display side by side with genre dropdown

            # Sub-container for dropdown and word bank
            html.Div([
                html.Label("Select genres:"), # label so users know what the dropdown is for
                html.Div([
                    dcc.Dropdown(
                        options=dropdown_options,
                        id='genre-dropdown',
                        placeholder='Select genre value(s)', # default value
                        multi=True, # allows for multiple genre values to be chosen
                        value=[option['value'] for option in dropdown_options],  # set default value to all genres
                        style={'width': '100%', 'maxHeight': '200px', 'overflowY': 'auto', 'margin-bottom' : '10px'} 
                    )
                ]), 

                html.Div([
                    html.Label("Color Word Bank:"), # label so users know what the dropdown is for
                    html.Div(id='genre-word-bank', style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-bottom': '20px'}),
                ], style={'width': '100%', 'overflowX': 'auto'}),
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '50px'}),
        ], style={'width': '100%'}), # added style width: 100% to make it responsive
    ], style={'margin-bottom': '30px'}),

    # Container for heatmap and description
    html.Div([
        # Container for heatmap
        html.Div([
            html.H3("Feature Correlation Analysis"), # title for heatmap
            html.Img(id='heatmap-image', style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}), # take up half of the screen
        ]),
        # Container for description
        html.Div([
            html.Div(id='description-container', children=[
                html.P("This heatmap illustrates the correlation between different features of the dataset. Each cell in the heatmap represents the correlation coefficient between two features. A correlation coefficient close to 1 indicates a strong positive correlation, while a coefficient close to -1 indicates a strong negative correlation. A coefficient close to 0 indicates no correlation."),
            ], style={'position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)',
                      'text-align': 'center', 'padding': '10px', 'border': '2px solid #000', 'border-radius': '10px',
                      'background-color': 'rgba(255, 255, 255, 0.8)', 'z-index': '1'}),
        ], style={'position': 'absolute', 'width': '45%', 'right': '0', 'top': '50%', 'transform': 'translateY(-50%)'}),
    ], style={'width': '100%', 'position': 'relative', 'margin-bottom': '30px'}),

    # Container for scatter plot
    html.Div([
        html.H3("Data Distribution Scatterplot"), # title for scatter plot
        dcc.Graph(id='scatter-plot')
    ], style={'margin-bottom': '5px'}),

    # Layout for dropdown menus
    html.Div([
        html.Div([
            html.Label("Select y-axis value: "), # label so users know what the dropdown is for
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[{'label': col, 'value': col} for col in available_columns],
                value=available_columns[1],  # default value to the second option
                style={'width': '90%'} 
            ),
        ], style={'display': 'inline-block', 'width': '49%'}), # take up half of the screen

        html.Div([
            html.Label("Select x-axis value: "), # label so users know what the dropdown is for
            dcc.Dropdown(
                id='x-axis-dropdown',
                options=[{'label': col, 'value': col} for col in available_columns],
                value=available_columns[0],  # default value to the first option
                style={'width': '90%'}
            ),
        ], style={'display': 'inline-block', 'width': '49%'}), # take up half of the screen
    ], style={'margin-bottom': '50px'}),

    # Paragraph at the bottom of the dashboard
    html.Div([
        html.H3(" "),
        html.H3("Data Overview"),
        html.H3(" "),
        html.P("This dataset used for this project shows a comprehensive summary of the music industry, presenting the top 10 songs from 2010 to 2019 globally. Collected from Spotify and Billboard, it shows current music trends in various areas and among various groups of people. Spotify is one of the biggest and popular applications people use for music streaming as both artists and producers release their singles, albums, and exclusive content through this platform. With a wide collection of data encompassing consumer preferences and listening habits, Spotify gives a valuable resource for understanding what drives viral hits in the music industry. The goal of this project is to take the insights from this dataset and create an interactive dashboard that will allow users to dive into different genres, styles, and the overall most popular songs throughout the world. This would provide personalized music recommendations based on the user preferences and give the opportunity for users to explore new songs. Although there were many other datasets available, this dataset specifically stood out because of its balance of depth and breadth of information which provides a solid basis for accomplishing my goal of this project. Thank you for taking the time to look through my dashboard!", style={'margin-top': '30px'})
    ]),
])

# Defining callback to update word cloud based on selected year and genre
@app.callback(
    Output('wordcloud-container', 'children'),
    [Input('year-slider', 'value'),
     Input('genre-dropdown', 'value')]
)
def update_wordcloud(selected_years, selected_genres):
    if selected_genres is None:
        # If no genre is selected, set selected_genres to all available genre values
        selected_genres = data['top genre'].unique()

    # Filtering data based on selected years and selected genre
    filtered_data = data[(data['year'] >= selected_years[0]) & (data['year'] <= selected_years[1]) &
                        (data['top genre'].isin(selected_genres))]

    # Extracting artist values and joining them while keeping multi-word names together
    preprocessed_artists = []
    for artist in filtered_data['artist']:
        artist = ' '.join(artist.split())
        preprocessed_artists.append(artist)

    # Defining color function
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        try:
            artist_genre = filtered_data.loc[filtered_data['artist'] == word, 'top genre'].iloc[0]
            return genre_color_map.get(artist_genre, 'black')  # returning color based on genre, default to black
        except IndexError:
            return 'black'  # if the artist doesn't have a genre, return black

    # Generating word cloud
    wordcloud = WordCloud(width=700, height=420, background_color='white', color_func=color_func).generate(' '.join(preprocessed_artists))

    # Rendering word cloud as an image in the app
    return html.Img(src=wordcloud.to_image())

# Defining callback to update genre word bank
@app.callback(
    Output('genre-word-bank', 'children'),
    [Input('wordcloud-container', 'children')]
)
def update_genre_word_bank(wordcloud): 
    genre_boxes = []
    for genre, color in genre_color_map.items():
        genre_boxes.append(html.Div(genre, style={'background-color': color, 'color': 'white', 'padding': '5px', 'display': 'inline-block', 'margin-right': '5px', 'margin-bottom': '5px', 'border-radius': '5px', 'font-size': '10px'})) # takes up 50% of the screen with each genre in 10 font 
    return genre_boxes

# Defining callback to update heatmap based on selected year
@app.callback(
    Output('heatmap-image', 'src'),
    [Input('year-slider', 'value')]
)
def update_heatmap(selected_years):
    # Filtering data based on selected years
    filtered_data = data[(data['year'] >= selected_years[0]) & (data['year'] <= selected_years[1])]

    # Calculating correlation matrix for numeric columns
    corr = filtered_data.iloc[:, 3:].corr()

    # Creating the heatmap
    f, ax = plt.subplots(figsize=(10, 10))
    cmap = "Blues"  # Using the blue color scale
    sns.heatmap(corr, cmap=cmap, vmax=.3, center=0, square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=False)

    # Saving the heatmap image to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=.3) 
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8') # encoding the image as a string

    # Returning the image data as a source for the html.Img component
    return 'data:image/png;base64,{}'.format(img_base64)

# Defining callback to update scatter plot based on selected x and y axis values and selected years
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('year-slider', 'value')]  
)
def update_scatter_plot(x_axis_value, y_axis_value, selected_years):
    # Filtering data based on selected years
    filtered_data = data[(data['year'] >= selected_years[0]) & (data['year'] <= selected_years[1])]

    # Creating a custom color scale of blues so it is the same as the heatmap
    custom_blues = ['#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5']

    # Creating scatter plot with the custom color scale
    fig = px.scatter(filtered_data, x=x_axis_value, y=y_axis_value, color=y_axis_value, hover_name='title', hover_data=['artist', 'year'],
                     color_continuous_scale=custom_blues)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)



