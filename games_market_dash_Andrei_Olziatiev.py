from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# загружаем данные из таблицы games.csv
df_games = pd.read_csv('games.csv')
# Заполним пропущенные значения 0
df_games.fillna({'Year_of_Release':0}, inplace=True)
# Приведем к числовому формату in
df_games['Year_of_Release'] = df_games['Year_of_Release'].astype(int)
# Приведем столбец User_Score к числовому формату и заполним ошибкочные значения NaN
df_games['User_Score'] = pd.to_numeric(df_games['User_Score'], errors='coerce')
# Исключаем проекты ранее 1990 и позднее 2010 годов и убираем строки с пропущенными значениями
data = df_games.query('1990 <= Year_of_Release <= 2010').dropna()
available_platform_filters = sorted(data['Platform'].unique())
available_genre = sorted(data['Genre'].unique())

# Инициализация приложения с использованием темы Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Аналитика видеоигр"

# Макет приложения
app.layout = html.Div([
    # Заголовок и описание
    html.Div([
        html.H1("Дашборд для анализа видеоигр", style={'textAlign': 'center'}),
        html.P(
            "Этот дашборд позволяет анализировать данные о видеоиграх. "
            "Вы можете использовать фильтры для выбора платформ, жанров и интервала годов выпуска. "
            "На основе этих данных отображаются ключевые метрики и интерактивные графики.",
            style={'textAlign': 'center', 'margin': '0 auto', 'maxWidth': '800px'}
        ),
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'}),

    # Фильтры
    dbc.Row([
        dbc.Col([
            html.Label("Фильтр платформ"),
            dcc.Dropdown(
                id='platform-filter',
                options=[{'label': platform, 'value': platform} for platform in available_platform_filters],
                multi=True,
                placeholder="Выберите платформы"
            ),
        ], width=4),
        dbc.Col([
            html.Label("Фильтр жанров"),
            dcc.Dropdown(
                id='genre-filter',
                options=[{'label': genre, 'value': genre} for genre in available_genre],
                multi=True,
                placeholder="Выберите жанры"
            ),
        ], width=4),
        dbc.Col([
            html.Label("Интервал годов выпуска"),
            dcc.RangeSlider(
                id='year-filter',
                min=data['Year_of_Release'].min(),
                max=data['Year_of_Release'].max(),
                step=1,
                marks={year: str(year) for year in range(data['Year_of_Release'].min(), data['Year_of_Release'].max() + 1, 5)},
                value=[data['Year_of_Release'].min(), data['Year_of_Release'].max()]
            ),
        ], width=4),
    ], style={'margin': '20px'}),

    # Метрики
    dbc.Row([
        dbc.Col(dbc.Card(html.Div(id='total-games'), body=True, color="info", inverse=True), width=4),
        dbc.Col(dbc.Card(html.Div(id='avg-player-score'), body=True, color="success", inverse=True), width=4),
        dbc.Col(dbc.Card(html.Div(id='avg-critic-score'), body=True, color="warning", inverse=True), width=4),
    ], style={'margin': '20px'}),

    # Графики
    dbc.Row([
        dbc.Col(dcc.Graph(id='age-rating-chart'), width=6),
        dbc.Col(dcc.Graph(id='scatter-plot'), width=6),
    ], style={'margin': '20px'}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='stacked-area-plot'), width=12),
    ], style={'margin': '20px'}),
])

# Коллбеки
@app.callback(
    [
        Output('total-games', 'children'),
        Output('avg-player-score', 'children'),
        Output('avg-critic-score', 'children'),
        Output('age-rating-chart', 'figure'),
        Output('scatter-plot', 'figure'),
        Output('stacked-area-plot', 'figure')
    ],
    [
        Input('platform-filter', 'value'),
        Input('genre-filter', 'value'),
        Input('year-filter', 'value')
    ]
)
def update_dashboard(selected_platforms, selected_genres, selected_years):
    # Фильтрация данных
    filtered_data = data[
        (data['Platform'].isin(selected_platforms) if selected_platforms else True) &
        (data['Genre'].isin(selected_genres) if selected_genres else True) &
        (data['Year_of_Release'].between(selected_years[0], selected_years[1]))
    ]
    
    # График 1: Общее число игр
    total_games = len(filtered_data)
    total_games_output = html.H5(f"Общее число игр: {total_games}", style={'textAlign': 'center'})
    
    # График 2: Средняя оценка игроков
    avg_player_score = filtered_data['User_Score'].mean()
    avg_player_score_output = html.H5(
        f"Средняя оценка игроков: {avg_player_score:.2f}" if not pd.isna(avg_player_score) else "Нет данных",
        style={'textAlign': 'center'}
    )
    
    # График 3: Средняя оценка критиков
    avg_critic_score = filtered_data['Critic_Score'].mean()
    avg_critic_score_output = html.H5(
        f"Средняя оценка критиков: {avg_critic_score:.2f}" if not pd.isna(avg_critic_score) else "Нет данных",
        style={'textAlign': 'center'}
    )
    
    # График 4: Число игр в каждой категории ESRB
    rating_counts = filtered_data.groupby('Rating').size().reset_index(name='Count')
    age_rating_chart = px.bar(
        rating_counts,
        x='Rating',
        y='Count',
        title="Распределение игр по категориям ESRB",
        labels={'Rating': 'Категория ESRB', 'Count': 'Количество игр'}
    )
    age_rating_chart.update_yaxes(rangemode='tozero')
    
    # График 5: Scatter plot
    scatter_plot = px.scatter(
        filtered_data,
        x='Critic_Score',
        y='User_Score',
        color='Genre',
        title="Оценки критиков и игроков",
        labels={'Critic_Score': 'Оценка критиков', 'User_Score': 'Оценка игроков'}
    )
    
    # График 6: Stacked area plot
    games_by_year_platform = filtered_data.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Count')
    stacked_area_plot = px.area(
        games_by_year_platform,
        x='Year_of_Release',
        y='Count',
        color='Platform',
        title="Выпуск игр по годам и платформам"
    )
    
    return total_games_output, avg_player_score_output, avg_critic_score_output, age_rating_chart, scatter_plot, stacked_area_plot

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
