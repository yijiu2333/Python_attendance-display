import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import os
from datetime import datetime
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# 定义考勤数据模型
class Attendance:
    def __init__(self, idnum, department, expected, actual, attendance_rate, absentees, remarks):
        self.idnum = idnum
        self.department = department
        self.expected = expected
        self.actual = actual
        self.attendance_rate = attendance_rate
        self.absentees = absentees
        self.remarks = remarks

# 定义全局状态
class AppState:
    def __init__(self):
        self.data = []  # 部门数据
        self.center_data = []  # 车间数据
        self.current_time = ""  # 当前时间
        self.day_in = 0  # 本日入职人数
        self.day_out = 0  # 本月离职人数
        self.sum_number = 0  # 总人数
        self.chart_data = []  # 图表数据
        self.male_number = 1000  # 男性员工人数（固定假数据）
        self.female_number = 1500  # 女性员工人数（固定假数据）

# 初始化全局状态
state = AppState()

# 定义条形图颜色函数
def generate_colors(data):
    colors = []
    for row in data:
        if row["value"] < 70:
            colors.append("#ffa09e") # 红色
        elif 70 <= row["value"] < 90:
            colors.append("#ffdca2") # 黄色
        else:
            colors.append("#a4ccff") # 绿色
    return colors

# 定义折线图边框颜色函数
def generate_line_colors(data):
    colors = []
    for row in data:
        if row["value"] < 70:
            colors.append("#C53B39") # 红色
        elif 70 <= row["value"] < 90:
            colors.append("#FFC300") # 黄色
        else:
            colors.append("#3498DB") # 蓝色
    return colors

# 定义主页面布局
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder='assets')
app.layout = html.Div(
    [
        # 顶部时间戳和标题
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url("logo.jpg"),
                    alt="Logo",
                    style={"width": "200px", "height": "auto", "margin": "1rem"},
                ),
                html.H1(
                    id="current-time",
                    children="",
                    style={"color": "#2d3748", "fontWeight": "bold", "marginBottom": "0.5rem"}
                ),
            ],
            style={"display": "flex",
                   "alignItems": "center",
                   "justifyContent": "space-between",
                    "padding": "1rem"}
        ),
        
        # 统计卡片
        html.Div(
            [
                # 总人数
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Img(src=app.get_asset_url("kehu.png"), style={"width": "50px", "height": "auto"}),
                            html.H4("总人数", className="card-title"),
                            html.H2(id="sum-number", children="", className="card-text"),
                        ]
                    ),
                    style={"backgroundColor": "#265589", 
                           "color": "#fdf5f3", 
                           "boxShadow": "0 4px 6px -11px rgba(10, 9, 60, 0.1)",
                           "width": "150px",
                           "padding": "0.5rem",
                           "borderRadius": "1rem",  # 设置圆角效果
                           "textAlign": "center",
                           "margin": "0.5rem"}
                ),
                
                # 本日入职人数
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Img(src=app.get_asset_url("zhuanshenren.png"), style={"width": "50px", "height": "auto"}),
                            html.H4("本日入职人数", className="card-title"),
                            html.H2(id="day-in", children="", className="card-text"),
                        ]
                    ),
                    style={"backgroundColor": "#8ea9c4", 
                           "color": "#fdf5f3", 
                           "boxShadow": "0 4px 6px -11px rgba(15, 83, 42, 0.1)",
                           "width": "150px",
                           "padding": "0.5rem",
                           "borderRadius": "1rem",  # 设置圆角效果
                           "textAlign": "center",
                           "margin": "0.5rem"}
                ),
                
                # 本月离职人数
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Img(src=app.get_asset_url("zhuanshenren.png"), style={"width": "50px", "height": "auto"}),
                            html.H4("本月离职人数", className="card-title"),
                            html.H2(id="day-out", children="", className="card-text"),
                        ]
                    ),
                    style={"backgroundColor": "#cbaea8", 
                           "color": "#fdf5f3", 
                           "boxShadow": "0 4px 6px -11px rgba(67, 11, 53, 0.1)",
                           "width": "150px",
                           "padding": "0.5rem",
                           "borderRadius": "1rem",  # 设置圆角效果
                           "textAlign": "center",
                           "margin": "0.5rem"}
                ),
            ],
            style={"display": "flex", "padding": "0.5rem"}
        ),
        
        html.Div(
            [
                html.H3("各部门人数分布"),
                html.Div(
                    [
                        # 更新时间
                        dcc.Interval(
                            id='interval-component',
                            interval=5*1000, # 每5秒更新一次
                            n_intervals=0
                        ),
                        # 条形图
                        dcc.Graph(id='bar-chart'),
                    ],
                    style={
                        "overflow-x": "auto",  # 启用水平滚动
                        "whiteSpace": "nowrap",  # 防止内容换行
                        "padding": "1rem",
                        "margin": "auto",
                    }
                ),
            ],
            style={"padding": "1rem",
                   "margin": "auto",}
        ),

        # 表格部分
        html.Div(
            [
                # 车间数据表格
                html.Div(
                    [
                        html.H3("车间每日出勤"),
                        html.Div(
                            dbc.Table(
                                id="center-table",
                                bordered=True,
                                hover=True,
                                responsive=True,
                                style={"width": "100%"},
                                striped=True,
                            ),
                            style={
                                "height": "420px",  # 设置固定高度
                                "overflowY": "auto",  # 超出部分显示滚动条
                                "-ms-overflow-style": "none",  # IE 和 Edge
                                "scrollbar-width": "none",     # Firefox
                            }
                        ),
                    ],
                    style={"width": "48%", 
                    "display": "inline-block", 
                    "verticalAlign": "top", 
                    "marginRight": "1rem"}
                ),
                
                # 部门数据表格
                html.Div(
                    [
                        html.H3("部门每日出勤"),
                        html.Div(
                            dbc.Table(
                                id="department-table",
                                bordered=True,
                                hover=True,
                                responsive=True,
                                style={"width": "100%"},
                                striped=True,
                            ),
                            style={
                                "height": "420px",  # 设置固定高度
                                "overflowY": "auto",  # 超出部分显示滚动条
                                "-ms-overflow-style": "none",  # IE 和 Edge
                                "scrollbar-width": "none",     # Firefox
                            }
                        ),
                    ],
                    style={"width": "48%", 
                    "display": "inline-block",
                    "verticalAlign": "top"}
                )
            ],
            style={"padding": "1rem"}
        ),

        html.Div(
            [
                html.H3("员工性别比例图"),
                html.Div(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Img(src=app.get_asset_url("nanshi.png"), style={"width": "50px", "height": "auto"}),
                                    html.H4("男性员工人数", className="card-title"),
                                    html.H2(id="male-number", children="", className="card-text"),
                                ]
                            ),
                            style={"backgroundColor": "#8ea9c4", 
                                "color": "#fdf5f3", 
                                "borderShadow": "0 14px 16px -11px rgba(10,9,60,0.1)",
                                "width": "200px",
                                "borderRadius": "1rem",  # 设置圆角效果
                                "margin": "0.5rem",
                                "padding": "0.5rem",
                                "textAlign": "center",},
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [   
                                    html.Img(src=app.get_asset_url("bailing.png"), style={"width": "50px", "height": "auto"}),
                                    html.H4("女性员工人数", className="card-title"),
                                    html.H2(id="female-number", children="", className="card-text"),
                                ]
                            ),
                            style={"backgroundColor": "#cbaea8", 
                                "color": "#fdf5f3", 
                                "borderShadow": "0 14px 16px -11px rgba(10,9,60,0.1)",
                                "width": "200px",
                                "borderRadius": "1rem",  # 设置圆角效果
                                "margin": "0.5rem",
                                "padding": "0.5rem",
                                "textAlign": "center",},
                        ),
                    ],
                    style={"display": "flex"}
                ),          
            ],
            style={"width": "45%",
                   "padding": "1rem"}
        ),
    ],
    style={
            "backgroundColor": "#fdf5f3",
            "height": "100vh",
            "maxWidth": "1500px"}
            
)

# 回调函数：更新当前时间
@app.callback(
    Output("current-time", "children"),
    Input("interval-component", "n_intervals")
)
def update_current_time(n):
    current_time = datetime.now().strftime("%Y年%m月%d日")
    return f"{current_time} 部门及车间考勤数据看板"

# 回调函数：加载数据并更新页面
@app.callback(
    [Output("bar-chart", "figure"),
     Output("sum-number", "children"),
     Output("day-in", "children"),
     Output("day-out", "children"),
     Output("center-table", "children"),
     Output("department-table", "children"),
     Output("male-number", "children"),
     Output("female-number", "children"),],
    Input("interval-component", "n_intervals")
)
def update_data(n):
    # 初始化数据
    state.data = []
    state.center_data = []
    state.sum_number = 0
    state.day_in = 0
    state.day_out = 0
    state.chart_data = []
    
    try:
        # 加载 Excel 数据
        data_path = "attendance.xlsx"
        df = pd.read_excel(data_path, skiprows=[0,40,41,42], engine='openpyxl')
        df_hrdata = pd.read_excel(data_path, engine='openpyxl')
        hrdata = df_hrdata.loc[40].tolist()
        
        state.sum_number = int(hrdata[2])
        state.day_in = int(hrdata[0])
        state.day_out = int(hrdata[1])

        # 加载 Excel 数据（这里仍使用假数据）
        state.male_number = 1000  # 男性员工人数（固定假数据）
        state.female_number = 1500  # 女性员工人数（固定假数据）
        
        # 生成图表数据
        state.chart_data = [{"name": str(row["部门"]), "value": int(row["应到人数"])} for _, row in df.iterrows()]
        
        # 筛选车间和部门数据
        mask = df["部门"].str.contains("车间")
        df_workshop = df[mask].sort_values(by="出勤率")
        df_other = df[~mask].sort_values(by="出勤率")
        
        # 车间数据
        state.center_data = [
            Attendance(
                i,
                row["部门"],
                row["应到人数"],
                row["实到人数"],
                round(row["出勤率"]*100, 2),
                row["缺勤人员姓名及原因"] if pd.notna(row["缺勤人员姓名及原因"]) else "",
                row["备注"] if pd.notna(row["备注"]) else "",
            )
            for i, row in df_workshop.iterrows()
        ]
        
        # 部门数据
        state.data = [
            Attendance(
                i,
                row["部门"],
                row["应到人数"],
                row["实到人数"],
                round(row["出勤率"]*100, 2),
                row["缺勤人员姓名及原因"] if pd.notna(row["缺勤人员姓名及原因"]) else "",
                row["备注"] if pd.notna(row["备注"]) else "",
            )
            for i, row in df_other.iterrows()
        ]
        
        # 生成图表
        bar_data = [{"name": row["name"], "value": row["value"]} for row in state.chart_data]
        fig = {
            "data": [{
                "x": [row["name"] for row in bar_data],
                "y": [row["value"] for row in bar_data],
                "type": "bar",
                "text": [f"{row['value']}人" for row in bar_data],
                "textposition": "auto",
                "marker": {"color": generate_colors(bar_data),
                           "line": {"width": 1.5, 
                                    "color": generate_line_colors(bar_data)}}
            }],
            "layout": {
                "title": "部门考勤情况",
                "height": 400,
                "width": 2500,  # 设置图表宽度为 50000
                "xaxis": {
                    "title": "部门",
                    "showgrid": True,
                    "autorange": True,
                    "showline": True,
                    "mirror": True,
                    "linecolor": "#7F7F7F",
                    "linewidth": 2,
                    "ticks": "outside",
                    "tickcolor": "#7F7F7F",
                    "ticklen": 10,
                    "tickwidth": 2,
                    "tickfont": {"size": 12},
                    "exponentformat": "none",
                    "showexponent": "all",
                    "side": "bottom",
                    "zeroline": False,
                    "zerolinecolor": "#7F7F7F",
                    "zerolinewidth": 2,
                    "gridcolor": "#E7E7E7",
                    "gridwidth": 1,
                    "tickangle": -45,
                    "automargin": True,
                },
                "yaxis": {
                    "title": "应到人数",
                    "showgrid": True,
                    "autorange": True,
                    "showline": True,
                    "mirror": True,
                    "linecolor": "#7F7F7F",
                    "linewidth": 2,
                    "ticks": "outside",
                    "tickcolor": "#7F7F7F",
                    "ticklen": 10,
                    "tickwidth": 2,
                    "tickfont": {"size": 12},
                    "exponentformat": "none",
                    "showexponent": "all",
                    "side": "left",
                    "zeroline": False,
                    "zerolinecolor": "#7F7F7F",
                    "zerolinewidth": 2,
                    "gridcolor": "#E7E7E7",
                    "gridwidth": 1
                },
                "bargap": 0.4,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#4a5568"},
                "margin": {"l": 40, "r": 40, "t": 40, "b": 100},
            }
        }
        
        # 生成车间表格
        center_table = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("车间", style={"minWidth": "100px", "textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("应到人数", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("实到人数", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("出勤率", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row.department, style={"fontWeight": "bold", "color": "#2d3748"}),
                            html.Td(row.expected, style={"textAlign": "center"}),
                            html.Td(row.actual, style={"textAlign": "center"}),
                            html.Td(
                                html.Div(
                                    f"{row.attendance_rate}%",
                                    style={
                                        "backgroundColor": "#4cb272" if row.attendance_rate >= 100 else "#f6e05e" if row.attendance_rate >= 70 else "red",
                                        "color": "white" if row.attendance_rate >= 100 else "#2d3748",
                                        "padding": "0.1em",
                                        "borderRadius": "4px",
                                        "textAlign": "center",
                                        #"display": "inline-block",  # 确保背景色只包裹内容
                                    }
                                ),
                            ),
                        ],
                        style={
                            "backgroundColor": "#E7E7E7" if i % 2 == 0 else "white",
                            # "fontWeight": "bold" if i == 0 else "normal",
                            "cursor": "pointer",
                        }
                    )
                    for i, row in enumerate(state.center_data)
                ]
            )
        ]
        
        # 生成部门表格
        department_table = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("部门", style={"minWidth": "100px", "textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("应到人数", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("实到人数", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                        html.Th("出勤率", style={"textAlign": "center", "backgroundColor": "#D8D7D7"}),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row.department, style={"fontWeight": "bold", "color": "#2d3748"}),
                            html.Td(row.expected, style={"textAlign": "center"}),
                            html.Td(row.actual, style={"textAlign": "center"}),
                            html.Td(
                                html.Div(
                                    f"{row.attendance_rate}%",
                                    style={
                                        "backgroundColor": "#4cb272" if row.attendance_rate >= 100 else "#f6e05e" if row.attendance_rate >= 70 else "red",
                                        "color": "white" if row.attendance_rate >= 100 else "#2d3748" if row.attendance_rate >= 70 else "white",
                                        "padding": "0.1em",
                                        "borderRadius": "4px",
                                        "textAlign": "center",
                                        #"display": "inline-block",  # 确保背景色只包裹内容
                                    }
                                ),
                            ),
                        ],
                        style={
                            "backgroundColor": "#D8D7D7" if i % 2 == 0 else "white",
                            # "fontWeight": "bold" if i == 0 else "normal",
                            "cursor": "pointer",
                        }
                    )
                    for i, row in enumerate(state.data)
                ]
            )
        ]

        # 生成男女比例饼图
        pie_fig = {
            "data": [go.Pie(
                labels=["Male", "Female"],
                values=[state.male_number, state.female_number],
                marker_colors=["#8ea9c4", "#cbaea8"],  # 柔和颜色
                textposition="inside",
                hole=0.4,
            )],
            "layout": {
                "title": "男女员工比例",
                "height": 300,
                "width": 300,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#4a5568"},
                "margin": {"l": 40, "r": 40, "t": 40, "b": 100},
                "showlegend": True,
                "legend": {"font": {"size": 14}},
            }
        }
        
        return (fig, state.sum_number, state.day_in, state.day_out, 
                center_table, department_table, state.male_number, 
                state.female_number)
    
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# 主程序
if __name__ == "__main__":
    # app.run(debug=True)
    app.run()