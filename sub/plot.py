import plotly.graph_objects as go
import vessel.draw as vd
import numpy as np
from plotly.subplots import make_subplots

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
    
def plot_fundamental(cond):
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