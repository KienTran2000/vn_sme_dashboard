import dash # type: ignore
from dash import dcc, html, Input, Output # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import json

# Load dữ liệu và bản đồ
df = pd.read_csv('sme_data.csv')
with open('vn_provinces.geojson', encoding='utf-8') as f:
    geojson = json.load(f)

# Khởi tạo ứng dụng
app = dash.Dash(__name__)
app.title = "Vietnam SME Dashboard"

# Giao diện
# Layout
app.layout = html.Div([
    html.H1("Vietnam SME ICT Dashboard", style={'textAlign': 'center'}),

    html.Label("Chọn năm:"),
    dcc.RangeSlider(
        id='year-slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        marks={i: str(i) for i in range(df['Year'].min(), df['Year'].max() + 1)},
        value=[df['Year'].min(), df['Year'].max()]
    ),

    html.Br(),
    html.Label("Lọc theo ngành:"),
    dcc.Dropdown(
        id='sector-filter',
        options=[{'label': s, 'value': s} for s in df['Sector'].unique()],
        value=None,
        placeholder="Chọn ngành nghề..."
    ),

    html.Br(),

    #html.Div([
    #    dcc.Graph(id='map', style={'width': '60%','height': '700px','display': 'inline-block', 'verticalAlign': 'top'}),
    #    dcc.Graph(id='bar', style={'width': '38%','height': '700px', 'display': 'inline-block', 'verticalAlign': 'top'}),
    #])
    html.Div([
    dcc.Graph(
        id='map',
        config={'scrollZoom': True},  # cho phép cuộn zoom
        style={
            'width': '60%',
            'height': '700px',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'cursor': 'pointer'  # con trỏ ngón tay
        }
    ),
    dcc.Graph(
        id='bar',
        style={
            'width': '38%',
            'height': '700px',
            'display': 'inline-block',
            'verticalAlign': 'top'
        }
    ),
])
])


# Callback cập nhật biểu đồ
@app.callback(
    [Output('map', 'figure'),
     Output('bar', 'figure')],
    [Input('year-slider', 'value'),
     Input('sector-filter', 'value')]
)
def update_dashboard(year_range, sector):
    dff = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    if sector:
        dff = dff[dff['Sector'] == sector]
    
    df_map = dff.groupby('Province', as_index=False)['CNTT_Used'].sum()
    map_fig = px.choropleth_mapbox(
        df_map,
        geojson=geojson,
        locations='Province',
        color='CNTT_Used',
        featureidkey="properties.name",
        mapbox_style="carto-positron",
        center={"lat": 15.0, "lon": 107.5},
        zoom=4.0,
        color_continuous_scale="Viridis",
        title="Tỷ lệ SME sử dụng CNTT theo tỉnh"
    )

    df_bar = dff.groupby('Technology')['CNTT_Used'].sum().reset_index()
    bar_fig = px.bar(df_bar, x='Technology', y='CNTT_Used', title="Số SME theo loại công nghệ")

    return map_fig, bar_fig


# Chạy server
if __name__ == '__main__':
    app.run(debug=True)
