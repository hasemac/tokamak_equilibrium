import plotly.graph_objects as go
import vessel.draw as vd

def d_contour(d_mat: dict):
    contour(d_mat['matrix'], d_mat['rmin'], d_mat['zmin'], d_mat['dr'], d_mat['dz'])

def contour(data, xmin, ymin, dx, dy):
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
                        shapes = vd.vac
                        )
    fig = go.Figure(data=data, layout=layout)
    fig.show()

def d_heatmap(d_mat: dict):
    heatmap(d_mat['matrix'], d_mat['rmin'], d_mat['zmin'], d_mat['dr'], d_mat['dz'])
         
def heatmap(data, xmin, ymin, dx, dy):
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
                    shapes = vd.vac
                    )
    fig = go.Figure(data=data, layout=layout)
    fig.show()    