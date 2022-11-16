import plotly
import plotly.graph_objects as go
import vessel.draw as vd
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

def line_plot(points, shapes = vd.vac):
    aspect = 2.0
    margin = 50
    width = 250
    
    r = [np.sqrt(e[0]**2+e[1]**2) for e in points]
    z = [e[2] for e in points]

    data = go.Scatter(x=r, y=z)
    layout = go.Layout(
        width = width + 2*margin,
        height = width*aspect + 2*margin,
        margin = dict(l=margin, r=margin, t=margin, b=margin, autoexpand=False),
        xaxis=dict(title='R(m)'), 
        yaxis=dict(title='z(m)', scaleanchor='x'),
        shapes = vd.vac
        )
    fig = go.Figure(data=data, layout=layout)
    fig.show()    

def line_plot3d(points):
    df = pd.DataFrame(points, columns=['x(m)', 'y(m)', 'z(m)'])
    fig = px.line_3d(df, 
                     x="x(m)", y="y(m)", z="z(m)", 
                     range_x=[-1.5, 1.5], 
                     range_y=[-1.5, 1.5], 
                     range_z=[-1.1, 1.1],
                     )
    fig.show()

def d_contour(d_mat: dict):
    contour(d_mat['matrix'], d_mat['rmin'], d_mat['zmin'], d_mat['dr'], d_mat['dz'])

def contour(data, xmin, ymin, dx, dy, shapes = vd.vac):
    """contour plot

    Args:
        data (2d array of float): data
        xmin (float): xmin
        ymin (float): ymin
        dx (foat): dx
        dy (float): dy
        shapes (lines, optional): _description_. Defaults to vd.vac.
    """
    (h, w)=data.shape
    h *=dy
    w *= dx
    #print(height, ' ', width)
    aspect = h/w
    margin = 50
    width = 250    
    
    data=go.Contour(z = data,
                    x0 = xmin, y0=ymin, dx=dx, dy=dy, 
                    showscale=False,
                    contours_coloring='lines',
                    #autocontour=True,
                    ncontours=100,
                    )

    layout = go.Layout( 
                        width = width+2*margin,
                        height = width*aspect+2*margin,
                        margin = dict(l=margin, r=margin, t=margin, b=margin, autoexpand=False),
                        xaxis=dict(
                            title='R(m)',
                            #range=(0, 1.8),
                            #scaleanchor='y',
                            #scaleratio = 1.0,
                            ),
                        yaxis=dict(
                            title='z(m)',
                            #range=(-1.8, 1.8), 
                            scaleanchor='x', 
                            #scaleratio = 1.0
                            ),
                        #shapes = [dict(type="line", x0=0,y0=0.0,x1=1.0,y1=1.83), dict(type="line", x0=1.5,y0=0.0,x1=1.0,y1=1.83)],
                        shapes = shapes
                        )
    fig = go.Figure(data=data, layout=layout)
    fig.show()

def d_heatmap(d_mat: dict, shapes=vd.vac):
    heatmap(d_mat['matrix'], d_mat['rmin'], d_mat['zmin'], d_mat['dr'], d_mat['dz'], shapes=shapes)
         
def heatmap(data, xmin, ymin, dx, dy, shapes=vd.vac):
    (h, w)=data.shape
    h *=dy
    w *= dx
    aspect = h/w
    margin = 50
    width = 250      
    data=go.Heatmap(z = data,
                    x0 = xmin, y0=ymin, dx=dx, dy=dy, 
                    showscale=False,
                    )
    layout = go.Layout( 
                    width = width+2*margin,
                    height = width*aspect+2*margin,
                    margin = dict(l=margin, r=margin, t=margin, b=margin, autoexpand=False),
                    xaxis=dict(
                        title='R(m)',
                        #range=(0, 1.8),
                        ),
                    yaxis=dict(
                        title='z(m)',
                        #range=(-1.8, 1.8), 
                        scaleanchor='x', 
                        #scaleratio = 1.0
                        ),
                    #shapes = [dict(type="line", x0=0,y0=0.0,x1=1.0,y1=1.83), dict(type="line", x0=1.5,y0=0.0,x1=1.0,y1=1.83)],
                    shapes = shapes
                    )
    fig = go.Figure(data=data, layout=layout)
    fig.show()

# インタラクティブプロット　共通x, 複数y: yは2次元arrayであることに注意
def iplot_df(
    df, labels = None, 
    xlabel = None, ylabel = None,
    xrange = None, yrange = None, 
    yaxis_type='linear', 
    title=None,
    width=600, height=400,
    mode='lines',
    showlegend = True, legend_title=None, legend=None, 
    draw = True
    ):
    # arrayY = [[ch1], [ch2],,,,,]
    # xrange = [0, 10], yrange = [10, 20]
    # xaxis_type: 自動判別、datetimeの時'linear'だと表示されない。
    # yaxis_type: 'linear', 'log', etc.
    # mode: 'lines', 'markers', 'lines+markers', or ['lines', 'markers', ]
    # legend = {"x":0.02, "y":0.95}
    # draw = True: グラフを描画して何も返さない。
    # draw = False: グラフを描画しないでグラフを返す。 
    #showlegend = True
    if labels == None:
        #labels = [''] * len(df.columns)
        labels = df.columns
        #showlegend = False
    modes = []
    if type(mode) != list:
        modes = [mode] * len(df.columns)
    else:
        modes = mode

    plotly.offline.init_notebook_mode(connected=False)
    dat = []
    for i in range(len(df.columns)):
        dat.append(plotly.graph_objs.Scatter(x = df.index, y = df.iloc[:,i], mode=modes[i], name=labels[i]))

    lay = plotly.graph_objs.Layout(
    showlegend=showlegend,        
    title=title,
    legend=legend,
    #legend={"x":0.02, "y":0.95},
    #xaxis_type=xaxis_type,
    legend_title=legend_title,
    yaxis_type=yaxis_type,
    xaxis={"title":xlabel, 'range':xrange},
    yaxis={"title":ylabel, 'range':yrange, 'showgrid':None},
    width=width, height=height
    )

    fig = plotly.graph_objs.Figure(data=dat, layout=lay)
    if draw:
        plotly.offline.iplot(fig)
    else:
        #plotly.io.write_image(fig, 'c://home/data/text.png')
        return fig
    
def plot_fundamental_nf(cond):
    def add_trace(fig, x, y, row, col, ylabel=''):
        fig.add_trace(go.Scatter(x=x, y=y), row=row, col=col)
        fig.update_yaxes(title_text=ylabel, row=row, col=col)
        
    fig = make_subplots(rows=2, cols=2)
        
    y0 = cond['diff_pre_norm']
    x = np.linspace(0, 1, len(y0))
    add_trace(fig, x, y0, 1, 1, ylabel='(dp/df)[x]')

    y1 = cond['pressure_norm']
    add_trace(fig, x, y1, 1, 2, ylabel='p[x]')

    y2 = cond['diff_i2_norm']
    add_trace(fig, x, y2, 2, 1, ylabel='(di^2/df)[x]')

    y3 = cond['pol_current_norm']
    add_trace(fig, x, y3, 2, 2, ylabel='i[x]')

    fig.update_layout(height=600, width=800)
    fig.show()
    
def plot_fundamental(cond):
    def add_trace(fig, x, y, row, col, xlabel='', ylabel=''):
        fig.add_trace(go.Scatter(x=x, y=y), row=row, col=col)
        fig.update_yaxes(title_text=ylabel, row=row, col=col)
        fig.update_xaxes(title_text=xlabel, row=row, col=col)
                
    fig = make_subplots(rows=3, cols=2)
        
    y0 = cond['diff_pre_norm']
    x = np.linspace(0, 1, len(y0))
    x1 = x*(cond['f_surf']-cond['f_axis'])+cond['f_axis']
    
    add_trace(fig, x1, y0, 1, 1, xlabel='flux', ylabel='(dp/df)[x]')

    y1 = cond['pressure_norm']
    add_trace(fig, x1, y1, 2, 1, xlabel='flux', ylabel='p[x]')

    y2 = cond['diff_i2_norm']
    add_trace(fig, x1, y2, 1, 2, xlabel='flux', ylabel='(di^2/df)[x]')

    y3 = cond['pol_current_norm']
    add_trace(fig, x1, y3, 2, 2, xlabel='flux', ylabel='i[x]')
    
    y5 = 2.0*np.pi*y0
    y6 = 10**(-7)*y2
    add_trace(fig, x1, y5, 3, 1, xlabel='flux', ylabel='2pi(dp/df)')
    add_trace(fig, x1, y6, 3, 2, xlabel='flux', ylabel='(u0/4pi)(di^2/df)')
    
    fig.update_layout(height=600, width=800)
    fig.show()

def plot_val(cond, name):
    y = cond[name]
    x = np.linspace(0, 1, len(y))
    df = pd.DataFrame(data=np.array([x, y]).T, columns=['norm flux', name])
    fig2 = px.line(df, x='norm flux', y=name, width=600, height=400)
    fig2.show()

def plot_gc(cond, name, time=True):
    if time:
        dat = np.array([cond['time'], cond[name]]).T
        df = pd.DataFrame(dat, columns=['time', name])
        fig = px.line(df, x='time', y=name, width=600, height=400)
    else:
        d0 = cond[name]
        dat = np.array([np.arange(0, len(d0)), d0]).T
        df = pd.DataFrame(dat, columns=['num', name])
        fig = px.line(df, x='num', y=name, width=600, height=400)
    fig.show()