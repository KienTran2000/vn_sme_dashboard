import dash  # type: ignore
from dash import dcc, html, Input, Output  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import json
from dash.dependencies import State
from dash import ctx

# Load dữ liệu và bản đồ
df = pd.read_csv('sme_data.csv')
with open('vn_provinces.geojson', encoding='utf-8') as f:
    geojson = json.load(f)

# Khởi tạo ứng dụng
app = dash.Dash(__name__)
app.title = "Vietnam SME Dashboard"

# Giao diện (Layout)
app.layout = html.Div([
    html.H1("🌟 Vietnam SME ICT Dashboard 🌟", style={
        'textAlign': 'center',
        'fontFamily': 'Segoe UI',
        'fontWeight': '700',
        'fontSize': '36px',
        'marginBottom': '15px',
        'color': '#1f2937',
        'transition': 'all 0.5s ease-in-out'
    }),

    html.Div([
        html.Label("📅 Select Year:", style={'fontWeight': 'bold', 'color': '#111827'}),
        dcc.RangeSlider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            marks={i: str(i) for i in range(df['Year'].min(), df['Year'].max() + 1)},
            value=[df['Year'].min(), df['Year'].max()],
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),

        html.Div([
            html.Label("🏢 Filter by Industry:", style={'fontWeight': 'bold', 'color': '#111827'}),
            dcc.Dropdown(
                id='sector-filter',
                options=[{'label': s, 'value': s} for s in df['Sector'].unique()],
                value=None,
                placeholder="Choose a profession...",
                style={'backgroundColor': '#ffffff'}
            )
            ], style={'width': '49%', 'display': 'inline-block', 'paddingRight': '1%'}),
        
        html.Div([
            html.Label("💻 Filter by Technology:", style={'fontWeight': 'bold', 'color': '#111827'}),
            dcc.Dropdown(
                    id='tech-filter',
                    options=[{'label': t, 'value': t} for t in df['Technology'].unique()],
                    value=None,
                    placeholder="Choose technology...",
                    style={'backgroundColor': '#ffffff'},
                    multi=True
            )
        ], style={'width': '49%', 'display': 'inline-block'}),

        html.Br(),
        html.Div([
                html.Label("🏗️ Enterprise Size:", style={'fontWeight': 'bold', 'color': '#111827'}),
                dcc.Dropdown(
                        id='size-filter',
                        options=[{'label': s, 'value': s} for s in df['FirmSize'].unique()],
                        value=None,
                        placeholder="Choose scale...",
                        style={'backgroundColor': '#ffffff'},
                        multi=True
                )
                ], style={'width': '49%', 'display': 'inline-block', 'paddingRight': '1%'}),

    # DISPLAY MODE
    html.Div([
        html.Label("📊 Display Mode:", style={
            'fontWeight': 'bold',
            'color': '#111827',
            'display': 'block',       
        }),
        html.Div([
            dcc.RadioItems(
                id='display-mode',
                options=[
                    {'label': '🧮 Number of SMEs Using ICT', 'value': 'CNTT_Used'},
                    {'label': '⚙️ Productivity', 'value': 'Productivity'}
                ],
                value='CNTT_Used',
                labelStyle={'display': 'inline-block', 'marginRight': '25px'},
                inputStyle={"marginRight": "8px"},
            )
        ], style={
            'border': '1px solid #ccc',
            'borderRadius': '4px',
            'padding': '10px 12px',
            'backgroundColor': '#ffffff',
            'height': '36px',
            'boxSizing': 'border-box',
            'display': 'flex',
            'alignItems': 'center',
            'width': '100%'
        })
    ], style={
        'width': '49%',
        'display': 'inline-block',
        'verticalAlign': 'top'
    }),

    html.Div([
            html.Button("📥 Download CSV Data", id="download-btn")
    ], style={
            'marginTop': '16px',
            'width': '100%',
            'textAlign': 'left'  # hoặc 'center' nếu muốn căn giữa
}),

        dcc.Download(id="download-data"),
    ], style={
        'width': '100%',
        'margin': 'auto',
        'padding-bottom': '5px',
        'backgroundColor': '#e0f2fe',
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.05)',
        'transition': 'all 0.4s ease-in-out'
    }),
    html.Br(),

    html.Div([
        dcc.Graph(id='map', 
            config={'scrollZoom': True},  # cho phép cuộn zoom      
            style={
            'width': '60%',
            'height': '650px',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'transition': 'transform 0.3s ease-in-out',
            'cursor': 'pointer'  # con trỏ ngón tay
        }),

        dcc.Graph(id='bar', style={
            'width': '38%',
            'height': '650px',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'marginLeft': '2%',
            'transition': 'transform 0.3s ease-in-out'
        })
    
    ],

    style={
        'width': '100%',
        'margin': 'auto',
        'paddingBottom': '50px'
    }),
], style={
    'backgroundColor': '#f0f9ff',
    'fontFamily': 'Segoe UI',
    'padding': '30px',
    'transition': 'all 0.4s ease-in-out'
})


# Callback cập nhật biểu đồ
@app.callback(
    [Output('map', 'figure'),
     Output('bar', 'figure')],
    [Input('year-slider', 'value'),
     Input('sector-filter', 'value'),
     Input('tech-filter', 'value'),     # <== thêm input này
     Input('size-filter', 'value'), 
     Input('display-mode', 'value'),     
     ]
)

def update_dashboard(year_range, sector, tech, size, display_mode):
    dff = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    if sector:
        dff = dff[dff['Sector'] == sector]
    if tech:
        dff = dff[dff['Technology'].isin(tech)]    # <== lọc công nghệ
    if size:
        dff = dff[dff['FirmSize'].isin(size)]      # <== lọc quy mô
    # Nếu đang chọn năng suất mà không có cột 'Productivity', hiển thị rỗng
    if display_mode == 'Productivity' and 'Productivity' not in dff.columns:
        return {}, {}

    # Map
    df_map = dff.groupby('Province', as_index=False)[display_mode].mean()
    map_fig = px.choropleth_mapbox(
        df_map,
        geojson=geojson,
        locations='Province',
        color=display_mode,
        featureidkey="properties.name",
        mapbox_style="carto-positron",
        center={"lat": 15.0, "lon": 107.5},
        zoom=4.0,
        color_continuous_scale="Viridis",
        title="	SME Rate by Province" if display_mode == 'CNTT_Used' else "Productivity by province",
        hover_data=['Province']
    )

    # Bar

    df_bar = dff.groupby(['Year', 'Technology'], as_index=False)[display_mode].mean()
    bar_fig = px.bar(
        df_bar,
        x='Technology',
        y=display_mode,
        animation_frame='Year',  # << thêm dòng này
        title="📊 Number of SMEs by Technology" if display_mode == 'CNTT_Used' else "⚙️ Productivity by Technology",
            color='Technology',  # Group theo công nghệ để tạo màu
    color_discrete_map={
        'AI': '#86efac',        # xanh lá pastel
        'CRM': '#fca5a5',       # đỏ hồng
        'Cloud': '#a5b4fc',     # xanh dương nhạt
        'ERP': '#f9a8d4'        # hồng nhẹ
    }
    )
    
    bar_fig.update_layout(
    updatemenus=[{
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 1500, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 500}}],
                "label": "▶️",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "⏹",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 70},
        "showactive": True,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }],
    sliders=[{
        "transition": {"duration": 500},
        "pad": {"b": 10},
        "currentvalue": {"prefix": "Year="},
        "len": 0.9
    }]
)

    return map_fig, bar_fig
@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    State("year-slider", "value"),
    State("sector-filter", "value"),
    State("tech-filter", "value"),
    State("size-filter", "value"),
    prevent_initial_call=True
)
def download_data(n_clicks, year_range, sector, tech, size):
    dff = df.copy()
    dff = dff[(dff['Year'] >= year_range[0]) & (dff['Year'] <= year_range[1])]
    if sector:
        dff = dff[dff['Sector'] == sector]
    if tech:
        dff = dff[dff['Technology'].isin(tech)]
    if size:
        dff = dff[dff['FirmSize'].isin(size)]

    # Trả về file CSV đúng kiểu cho dash
    return dcc.send_data_frame(dff.to_csv, "filtered_data.csv")


# Chạy server
if __name__ == '__main__':
    app.run(debug=True)
