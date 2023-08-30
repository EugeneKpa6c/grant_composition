import dash
from dash import Dash, dash_table, clientside_callback, Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import psycopg2
import pandas as pd
import plotly.graph_objs as go
import requests, cv2
import numpy as np
from boxannotator import BoxAnnotator
from io import BytesIO
import base64
import logging
from PIL import Image
import io
import imageio
from test_vcl import Recorder, find_camera_ip

logging.basicConfig(level=logging.INFO)

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/_dashboard-one.css', 'assets/_header.css', 'assets/time.css'])

video_stream = html.Iframe(src="http://10.10.136.59:8000/client/webrtc.html", width="100%", height="722px", style={"overflow-y": "hidden"})
# video_stream = html.Iframe(src="https://localhost:8001/client/webrtc.html", width="100%", height="722px", style={"overflow-y": "hidden"})


@app.callback(
    [
        Output('video-container', 'children'),
        Output('original', 'className'),
        Output('oversized', 'className'),
        Output('structure', 'className')
    ],
    [
        Input('original', 'n_clicks'),
        Input('oversized', 'n_clicks'),
        Input('structure', 'n_clicks')
    ],
    [
        State('original', 'className'),
        State('oversized', 'className'),
        State('structure', 'className')
    ]
)
def update_video_stream(original_clicks, oversized_clicks, structure_clicks, original_class, oversized_class, structure_class):
    
    default_class = "btn"
    active_class = "btn active"

    # Инициализация значениями по умолчанию
    new_original_class = default_class
    new_oversized_class = default_class
    new_structure_class = default_class
    current_stream = video_stream

    # определите, какая кнопка была нажата последней
    ctx = dash.callback_context
    if not ctx.triggered:
        return video_stream, active_class, default_class, default_class
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if btn_id == "original":
        current_stream = html.Iframe(src="https://localhost:8001/client/webrtc.html", width="100%", height="722px", style={"overflow-y": "hidden"})
        new_original_class = active_class
    elif btn_id == "oversized":
        current_stream = html.Img(src='/assets/1.png', style={"width": "100%", "height": "722px"})
        new_oversized_class = active_class
    elif btn_id == "structure":
        current_stream = html.Img(src='/assets/2.png', style={"width": "100%", "height": "722px"})
        new_structure_class = active_class

    return current_stream, new_original_class, new_oversized_class, new_structure_class


@app.callback(
    Output('stream-container', 'children'),
    [Input('graphs-link', 'n_clicks'),
     Input('camera-link', 'n_clicks')]
)

def toggle_stream_visibility(graphs_clicks, camera_clicks):
    # определите, какая кнопка была нажата последней
    ctx = dash.callback_context
    if not ctx.triggered:
        return [stream]  # Показать Stream по умолчанию
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if btn_id == "graphs-link":
        return [graphs]  # Очистить Stream при нажатии на "Аналитика"
    elif btn_id == "camera-link":
        return [stream]  # Показать Stream при нажатии на "Камера"
    

import subprocess

# Global variable to hold the ffmpeg process
recorder = Recorder()

@app.callback(
    [Output('ffmpeg-button', 'color')],
    [Input('ffmpeg-button', 'n_clicks')]
)
def manage_ffmpeg(n_clicks):
    if n_clicks % 2 == 1:
        camera_name = "axis-b8a44f0899b0"
        camera_ip = find_camera_ip(camera_name)
        if camera_ip:
            print(f"IP-адрес камеры {camera_name}: {camera_ip}")
            recorder.start_recording(camera_ip)
            print('Запись началась')
        else:
            print(f"Камера {camera_name} не найдена.")
        return ['danger']
    else:
        recorder.stop_recording()
        return ['primary']


# ffmpeg_process = None
# def manage_ffmpeg(n_clicks):
#     global ffmpeg_process
#     if n_clicks % 2 == 1:
#         # Start the ffmpeg process
#         ffmpeg_process = subprocess.Popen(
#             ['ffmpeg', '-i', 'rtsp://root:admin@10.10.132.21/axis-media/media.amp', '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', 'C:/Users/ivanin.em/Desktop/dashboard/assets/video/output.avi'],     
#         )
#         return ['danger']  
#     else:
#         if ffmpeg_process:
#             ffmpeg_process.send_signal(subprocess.signal.SIGTERM)  
#         return ['primary']  


navbar_content = html.Div(
    className="az-dashboard-nav",
    children=[
        html.Nav(
            className="nav",
            children=[
                html.Button("Камера", className="nav-link active", id="camera-link"),
                html.Button("Аналитика", className="nav-link", id="graphs-link"),
                html.Button("Что-то еще", className="nav-link", id="something-link"),
                html.Button("и еще", className="nav-link", id="another-link")
            ]
        ),
        html.Nav(
            className="nav",
            children=[
                html.A([html.I(className="far fa-save"), "Скачать"], className="nav-link", href="/"),
                html.A([html.I(className="far fa-file-pdf"), "Что-то еще"], className="nav-link", href="/"),
                html.A([html.I(className="far fa-envelope"), "и еще"], className="nav-link", href="/"),
                html.A([html.I(className="fas fa-ellipsis-h")], className="nav-link", href="/")
            ]
        )
    ]
)

line_style = {
    "display": "flex", 
    "align-items": "center", 
    "justify-content": "center",
    "border-right": "1px solid #ddd", 
    "padding-right": "15px", 
    "height": "50px"
}

header_content = html.Div(className="az-menu-sub-mega", children=[
    html.Div(className="az-notification-list", children=[
        html.Div(className="az-content-header-right", style={"display": "flex", "align-items": "center"}, children=[
            html.Div(className="media", style=line_style, children=[
                html.Div(className="media-body", children=[
                    html.Label("ДАТА", style={"color": "#888888", "fontSize": "10px", "fontWeight": "bold"}),
                    html.H6(id='current-date')
                ])
            ]),
            html.Div(className="media", style={"padding-right": "10px", "margin-right": "10px", "fontWeight": "bold"}, children=[
                html.Div(className="media-body", children=[
                    html.Label("ВРЕМЯ", style={"color": "#888888", "fontSize": "10px"}),
                    html.H6(id='current-time')
                ])
            ]),
            # html.A("Отчёт", href="", className="btn btn-outline-primary")
            dbc.Button("Сохранить", id="ffmpeg-button", color="primary", n_clicks=0)
        ])
    ])
])

stream =    html.Div(className="row row-sm mg-b-20", children=[
                html.Div(className="col-lg-12 ht-lg-100p", style={"marginBottom": "50px"}, children=[
                    html.Div(className="card card-dashboard-one", children=[
                        html.Div(className="card-header", children=[
                            html.Div(children=[
                                html.H6(className="card-title", children="Сменить вид"),
                                html.P(className="card-text", children="Возможность переключаться между камерой и результатом работы модели")
                            ]),
                            html.Div(className="btn-group", children=[
                                html.Button("Оригинал", id="original", className="btn active"),
                                html.Button("Негабарит", id="oversized", className="btn"),
                                html.Button("Состав", id="structure", className="btn"),
                            ])
                        ]),
                        html.Div(className="card-body",id='video-container', children=[
                            video_stream
                        ])
                    ])
                ]),
            ])
# Возвращает <count> последних уникальных негабаритов
def get_last_oversized(count):
    '''
    count - количество выводимых строк последних негабаритов
    '''
    # Подключение к БД
    connection = psycopg2.connect(user="postgres", 
                            password="postgres", 
                            # host="10.10.140.46",
                            host="localhost",
                            # host="postgres",
                            port="5433",
                            # database="postgres"
                            database="grant_composition") 

    cursor = connection.cursor()
    db = cursor.callproc('get_latest_images', (int(count),))
    data = cursor.fetchall()

    # columns = ['Индефикатор', 'Дата и время(МСК)']
    columns = ['Индификатор', 'Дата и время(МСК)', 'Класс']
    # Создаем список словарей, где каждый словарь представляет одну строку данных
    data_dict = {columns[i]: [row[i] for row in data] for i in range(len(columns))}
    # Создаем DataFrame из списка словарей
    df = pd.DataFrame(data_dict)
    cursor.close()
    connection.close()
    return df

df = get_last_oversized(10)

# Извлекаем id камня из столбца "Индефикатор" и добавляем его как новый столбец
# df['ID камня'] = df['Индефикатор'].apply(lambda x: int(x.split('-')[-1]))

# Создаем scatter plot
# scatter_figure_data = {
#     'data': [go.Scatter(x=df['Дата и время(МСК)'], y=df['ID камня'], mode='markers')],
#     'layout': go.Layout(xaxis_title='Дата и время', 
#                         yaxis_title='ID камня')
# }

video_frame = html.Img(id='video-frame', style={'width': '100%'})
video_interval = dcc.Interval(id='video-interval', interval=2500, max_intervals=-1)

def show_video(id_name):
    # Connecting to the DB using psycopg2
    connection = psycopg2.connect(user="postgres", 
                                  password="postgres", 
                                  host="localhost",
                                #   host="postgres",
                                  port="5433",
                                #   database="postgres"
                                database="grant_composition") 

    cursor = connection.cursor()
    db = cursor.callproc('get_link_and_xywh', (id_name,))
    data = cursor.fetchall()
    images_list = [item[0] for item in data]
    xywh_list = [item[1] for item in data]
    cursor.close()
    connection.close()
    
    images_and_xywh = {image: xywh for image, xywh in zip(images_list, xywh_list)}
    logging.info(images_and_xywh)
    return images_and_xywh
    # return images_list


last_stone_ids = get_last_oversized(10)['Индификатор'].tolist()

# Добавляем скрытый div для хранения списка изображений
image_list_div = html.Div(id='image-list-div', style={'display': 'none'})
previous_selected_id = html.Div(id='previous-selected-id', style={'display': 'none'})


def image_from_url_to_cv2(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    img = Image.open(io.BytesIO(response.content))
    image = np.array(img)

    return image

def cv2_image_to_dash(image):
    _, buffer = cv2.imencode('.png', image)
    image_as_bytes = buffer.tobytes()
    base64_encoded = base64.b64encode(image_as_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_encoded}"

@app.callback(
    Output('video-frame', 'src'), 
    Output('image-list-div', 'children'),
    Output('previous-selected-id', 'children'),
    Input('table', 'selected_cells'),
    Input('video-interval', 'n_intervals'),
    State('previous-selected-id', 'children')
)
def update_frame(selected_cells, n_intervals, previous_selected):
    if not selected_cells:
        return dash.no_update, dash.no_update, dash.no_update
    
    row = selected_cells[0]['row']
    column_id = selected_cells[0]['column_id']
    stone_id = df.iloc[row][column_id]
    # stone_id_str = str(stone_id)
    stone_id_str = int(stone_id)

    current_images_and_xywh = show_video(stone_id_str)
    if not current_images_and_xywh:
        return dash.no_update, [], dash.no_update
    
    current_image_keys = list(current_images_and_xywh.keys())
    current_image_index = n_intervals % len(current_image_keys)
    current_image_key = current_image_keys[current_image_index]
    current_xywh = current_images_and_xywh[current_image_key]

    # Сначала заменим обратные слэши на прямые (для унификации разделителей)
    path = current_image_key.replace("\\", "/")

    # Разбиваем строку по символу "/" и берем последний элемент
    filename = path.split("/")[-1]

    current_image_key = filename

    image_url = "http://localhost:8800/media/images/" + current_image_key
    # image_url = "http://10.10.136.59:8800/media/images/" + current_image_key
    logging.info(image_url)

    raw_image = image_from_url_to_cv2(image_url)
    annotated_image = BoxAnnotator().annotate(raw_image, current_xywh)
    image_for_dash = cv2_image_to_dash(annotated_image)

    return image_for_dash, current_images_and_xywh, stone_id_str



data = html.Div(children=[
    dcc.DatePickerRange(
        id="date-range-picker",
        start_date="2000-01-01",
        end_date="2000-01-30",
        min_date_allowed="2000-01-01",
        max_date_allowed="2000-01-30",
        display_format="YYYY-MM-DD",
        style={"marginBottom": "20px", "paddingTop": "20px"}
    )
])


@app.callback(
    [Output('start-hour-input', 'value'),
     Output('start-minute-input', 'value'),
     Output('start-hour-input', 'style'),
     Output('start-minute-input', 'style'),
     Output('end-hour-input', 'value'),
     Output('end-minute-input', 'value'),
     Output('end-hour-input', 'style'),
     Output('end-minute-input', 'style')],
    [Input('start-hour-input', 'value'),
     Input('start-minute-input', 'value'),
     Input('end-hour-input', 'value'),
     Input('end-minute-input', 'value')]
)

def correct_time_values(start_hour, start_minute, end_hour, end_minute):
    start_hour, start_minute, start_hour_style, start_minute_style = validate_time(start_hour, start_minute)
    end_hour, end_minute, end_hour_style, end_minute_style = validate_time(end_hour, end_minute)
    
    return start_hour, start_minute, start_hour_style, start_minute_style, end_hour, end_minute, end_hour_style, end_minute_style

def validate_time(hour, minute):
    hour_style = {"border": "2px solid #888888"}
    minute_style = {"border": "2px solid #888888"}

    if hour is not None:
        try:
            hour = int(hour)
            if hour > 23:
                hour = 23
                hour_style = {"border": "2px solid red"}
            elif hour < 0:
                hour = 0
                hour_style = {"border": "2px solid red"}
        except ValueError:
            if hour != "":
                hour = 0
                hour_style = {"border": "2px solid red"}
    else:
        hour = ""

    if minute is not None:
        try:
            minute = int(minute)
            if minute > 59:
                minute = 59
                minute_style = {"border": "2px solid red"}
            elif minute < 0:
                minute = 0
                minute_style = {"border": "2px solid red"}
        except ValueError:
            if minute != "":
                minute = 0
                minute_style = {"border": "2px solid red"}
    else:
        minute = ""

    return hour, minute, hour_style, minute_style


time_js = html.Script('''
    document.addEventListener('DOMContentLoaded', function() {
        function correctInputValue(input, max) {
            let value = parseInt(input.value);
            if (isNaN(value) || value > max) {
                input.value = max;
            } else if (value < 0) {
                input.value = 0;
            }
        }

        const hourInput = document.getElementById('hour-input');
        const minuteInput = document.getElementById('minute-input');

        hourInput.addEventListener('blur', function() {
            correctInputValue(hourInput, 23);
        });

        minuteInput.addEventListener('blur', function() {
            correctInputValue(minuteInput, 59);
        });
    });
''')



start_time_picker_elements = html.Div([
    html.Div(className="time-elements", children=[
        html.Label("Начальное время", style={"color": "#888888", "fontSize": "14px", "textAlign": "center"}),
        html.Div(className="time-picker", children=[
            dcc.Input(id="start-hour-input", type="text", maxLength=2, placeholder="HH", className="time-area"),
            html.Span(className="separator", children=":"),
            dcc.Input(id="start-minute-input", type="text", maxLength=2, placeholder="MM", className="time-area")
        ]),
        html.Div(className="error-message", id="start-time-error"),
        time_js
    ])
])

end_time_picker_elements = html.Div([
    html.Div(className="time-elements", children=[
        html.Label("Конечное время", style={"color": "#888888", "fontSize": "14px", "textAlign": "center"}),
        html.Div(className="time-picker", children=[
            dcc.Input(id="end-hour-input", type="text", maxLength=2, placeholder="HH", className="time-area"),
            html.Span(className="separator", children=":"),
            dcc.Input(id="end-minute-input", type="text", maxLength=2, placeholder="MM", className="time-area")
        ]),
        html.Div(className="error-message", id="end-time-error"),
        time_js
    ])
])




graphs = html.Div(id="graphs-container",className="row row-sm mg-b-20", children=[
    # Первая колонка
    html.Div(className="col-sm-7 ht-lg-100p", style={"marginBottom": "50px"}, children=[
        html.Div(className="card card-dashboard-one", style={"min-height": "549px"}, children=[
            html.Div(className="card-header", children=[
                html.Div(children=[
                    html.H6(className="card-title", children="Выбор временного отрезка"),
                    html.P(className="card-text", children="Возможность переключаться между 10-ю последними негабаритами или выбрать свой временной отрезок")
                ]),
                html.Div(className="btn-group", children=[
                    html.Button("10", id="ten", className="btn active"),
                    html.Button("~", id="all", className="btn"),
                ]),
            ]),
            html.Div(style={"width": "100%", "height": "100%", "paddingTop": "20px", "paddingLeft": "10px", "paddingRight": "10px", "marginBottom": "10px"}, children=[
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_table={'width': '100%', 'height': '100%'}
                )
            ]),
            html.Div(className="card-body", children=[
                html.Div(style={"width": "100%", "paddingTop": "5px", "paddingLeft": "10px", "paddingRight": "10px", "marginBottom": "10px"}, children=[
                    video_frame,
                    video_interval,
                    image_list_div,
                    previous_selected_id,
                ]),
            ]),
        ]),
    ]),
    # Вторая колонка
    html.Div(className="col-sm-5 ht-lg-100p", style={"marginBottom": "50px", "marginTop": "0px"}, children=[
        html.Div(className="card card-dashboard-one", children=[
            html.Div(className="card-header", children=[
                html.P("All Sessions"),
                html.H6(children=[
                    "16,869",
                    html.H6(children=[
                        " 2.87%", 
                        html.I(className="icon ion-md-arrow-up")
                    ], className="tx-success")
                ]),
                html.Small("Частота появления 10 последних негабаритов.")
            ]),
            # dcc.Graph(id='sessions-chart', figure=scatter_figure_data)
        ]),
    ]),
])


@app.callback(
    [
        Output('graphs-container', 'children'),
        Output('ten', 'className'),
        Output('all', 'className'),
    ],
    [
        Input('ten', 'n_clicks'),
        Input('all', 'n_clicks'),
    ],
    [
        State('ten', 'className'),
        State('all', 'className'),
    ]
)
def update_content(ten_clicks, all_clicks, ten_class, all_class):
    default_class = "btn"
    active_class = "btn active"

    # Content when "10" is active
    content_ten = html.Div(className="row row-sm mg-b-20", children=[
        # Первая колонка
        html.Div(className="col-sm-7 ht-lg-100p", style={"marginBottom": "50px"}, children=[
            html.Div(className="card card-dashboard-one", style={"min-height": "549px"}, children=[
                html.Div(className="card-header", children=[
                    html.Div(children=[
                        html.H6(className="card-title", children="Выбор временного отрезка"),
                        html.P(className="card-text", children="Возможность переключаться между 10-ю последними негабаритами или выбрать свой временной отрезок")
                    ]),
                    html.Div(className="btn-group", children=[
                        html.Button("10", id="ten", className="btn active"),
                        html.Button("~", id="all", className="btn"),
                    ]),
                ]),
                html.Div(style={"width": "100%", "height": "100%", "paddingTop": "20px", "paddingLeft": "10px", "paddingRight": "10px", "marginBottom": "10px"}, children=[
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        style_table={'width': '100%', 'height': '100%'}
                    )
                ]),
                html.Div(className="card-body", children=[
                    html.Div(style={"width": "100%", "paddingTop": "5px", "paddingLeft": "10px", "paddingRight": "10px", "marginBottom": "10px"}, children=[
                        video_frame,
                        video_interval,
                        image_list_div,
                        previous_selected_id,
                    ]),
                ]),
            ]),
        ]),
        # Вторая колонка
        html.Div(className="col-sm-5 ht-lg-100p", style={"marginBottom": "50px", "marginTop": "0px"}, children=[
            html.Div(className="card card-dashboard-one", children=[
                html.Div(className="card-header", children=[
                    html.P("All Sessions"),
                    html.H6(children=[
                        "16,869",
                        html.H6(children=[
                            " 2.87%", 
                            html.I(className="icon ion-md-arrow-up")
                        ], className="tx-success")
                    ]),
                    html.Small("Частота появления 10 последних негабаритов.")
                ]),
                # dcc.Graph(id='sessions-chart', figure=scatter_figure_data)
            ]),
        ]),
    ])

    # Content when "~" is active
    content_all = html.Div(className="row row-sm mg-b-20", children=[
        # First column with only the header and buttons
        html.Div(className="col-sm-7 ht-lg-100p", style={"marginBottom": "50px"}, children=[
            html.Div(className="card card-dashboard-one", style={"min-height": "549px"}, children=[
                html.Div(className="card-header", children=[
                    html.Div(children=[
                        html.H6(className="card-title", children="Выбор временного отрезка"),
                        html.P(className="card-text", children="Возможность переключаться между 10-ю последними негабаритами или выбрать свой временной отрезок")
                    ]),
                    html.Div(className="btn-group", children=[
                        html.Button("10", id="ten", className="btn"),
                        html.Button("~", id="all", className="btn active"),
                    ]),
                ]),
                html.Div(className="card-body", children=[
                    html.Div(style={
                            "width": "100%",
                            "paddingTop": "5px",
                            "paddingLeft": "10px",
                            "paddingRight": "10px",
                            "marginBottom": "10px",
                            "overflow": "visible",
                            "display": "flex",  # Add this line
                            "justifyContent": "space-between"  # This will add space between the elements
                        }, children=[
                        data,
                        start_time_picker_elements,
                        end_time_picker_elements
                    ]),
                ]),
            ]),
        ]),
        # Вторая колонка (remains the same)
        html.Div(className="col-sm-5 ht-lg-100p", style={"marginBottom": "50px", "marginTop": "0px"}, children=[
            html.Div(className="card card-dashboard-one", children=[
                html.Div(className="card-header", children=[
                    html.P("All Sessions"),
                    html.H6(children=[
                        "16,869",
                        html.H6(children=[
                            " 2.87%", 
                            html.I(className="icon ion-md-arrow-up")
                        ], className="tx-success")
                    ]),
                    html.Small("Частота появления 10 последних негабаритов.")
                ]),
                # dcc.Graph(id='sessions-chart', figure=scatter_figure_data)
            ]),
        ]),
    ])

    ctx = dash.callback_context
    if not ctx.triggered:
        return content_ten, active_class, default_class

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'ten':
        return content_ten, active_class, default_class
    elif button_id == 'all':
        return content_all, default_class, active_class





main_page = html.Div(id='stream-container', children=[stream, graphs])

content_layout = html.Div(className="az-content az-content-dashboard", children=[
    html.Div(className="container", children=[
        html.Div(className="az-content-body", children=[
            html.Div(className="az-dashboard-one-title", style={"flex-grow": "1"}, children=[
                html.Div(children=[
                    html.H2(className="az-dashboard-title", children="GV GOLD", style={"color":"blue"}),
                    html.P(className="az-dashboard-text", children="Аналитический дашборд")
                ]),
                header_content
            ]),
            navbar_content,
            main_page,
        ])
    ]),
dcc.Interval(id="date-interval", interval=60*1000, n_intervals=0),
html.Div(id="blank-output")])



app.layout = content_layout

clientside_callback(
    """
    function(n_intervals) {
        let now = new Date();
        let dateString = now.toLocaleDateString('ru', { month: 'short', day: '2-digit', year: 'numeric' });
        let timeString = now.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('current-date').textContent = dateString;
        document.getElementById('current-time').textContent = timeString;
    }
    """,
    Output('blank-output', 'children'),
    Input('date-interval', 'n_intervals')
)


if __name__ == '__main__':
    # app.run_server(host='10.10.136.59', port='8050', debug=True)
    app.run_server(host='0.0.0.0', port='8050', debug=False)