import dash  # type: ignore
from dash import dcc, html, Input, Output  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import json
from dash.dependencies import State
from dash import ctx
import plotly.express as px
import plotly.graph_objects as go  # 👈 thêm dòng này
import plotly.graph_objects as go
import plotly.express as px

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
                style={'backgroundColor': '#ffffff'},
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
    choropleth = px.choropleth_mapbox(
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
    map_fig = go.Figure(choropleth.data) # type: ignore

# Thêm các điểm scatter mapbox cho Hoàng Sa và Trường Sa
    map_fig.add_trace(go.Scattermapbox(
        lat=[16.8333, 11.6667],
        lon=[112.3167, 114.3333],
        mode='markers+text',
        marker=go.scattermapbox.Marker(size=10, color='red'),
        text=["Hoang Sa (Vietnam) ", "Truong Sa (Vietnam)"],
        textposition="top center",
        hoverinfo="text",
        name="Sovereign Islands"
    ))

# Kế thừa layout choropleth
    map_fig.update_layout(choropleth.layout)
    # Bar

    df_bar = dff.groupby(['Year', 'Technology'], as_index=False)[display_mode].mean()
    df_bar[display_mode] = df_bar[display_mode].fillna(0)
    # # Bar chart fix – đảm bảo đủ công nghệ mỗi năm
    # years = dff['Year'].unique()
    # technologies = df['Technology'].unique()  # dùng full tech từ toàn bộ data

    # # Tạo index đầy đủ
    # full_index = pd.MultiIndex.from_product([years, technologies], names=["Year", "Technology"])

    # # Group dữ liệu
    # df_bar = dff.groupby(['Year', 'Technology'], as_index=False)[display_mode].mean()

    # # Set index và reindex đầy đủ
    # df_bar = df_bar.set_index(['Year', 'Technology']).reindex(full_index, fill_value=0).reset_index()

    # # Đảm bảo cột display_mode vẫn tồn tại (phòng khi không có dòng nào ban đầu)
    # if display_mode not in df_bar.columns:
    #     df_bar[display_mode] = 0

    
    # bar_fig = px.bar(
    #     df_bar,
        
    #     x='Technology',
    #     y=display_mode,
        
    #     # animation_frame='Year',  # << thêm dòng này
    #     title="📊 Number of SMEs by Technology" if display_mode == 'CNTT_Used' else "⚙️ Productivity by Technology",
    #         color='Technology',  # Group theo công nghệ để tạo màu
    #     color_discrete_map={
    #         'AI': '#86efac',        # xanh lá pastel
    #         'CRM': '#fca5a5',       # đỏ hồng
    #         'Cloud': '#a5b4fc',     # xanh dương nhạt
    #         'ERP': '#f9a8d4'        # hồng nhẹ
    #     }
    #     ),
    

    # Line chart
    line_fig = px.line(
        df_bar,
        x='Year',
        y=display_mode,  
        color='Technology',
        markers=True,  # Có chấm tròn ở các điểm dữ liệu
        title="📈 Number of SMEs using IT by year",
        color_discrete_map={
            'AI': '#86efac',
            'CRM': '#fca5a5',
            'Cloud': '#a5b4fc',
            'ERP': '#f9a8d4',
            'Email': '#fdba74'
        }
    )

    line_fig.update_traces(mode="lines+markers")  # Đường có cả line + điểm
    line_fig.update_layout(
        title="📈 Productivity by Year" if display_mode == 'Productivity' else "📈 Number of SMEs using IT by year",
        xaxis_title="Years",
        yaxis_title="Productivity Score" if display_mode == 'Productivity' else "Number of SMEs by Technology",
        legend_title="Technology"
    )


    return map_fig, line_fig

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
