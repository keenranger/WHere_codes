import plotly.graph_objects as go

def plot_magnet(mag_df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mag_df['x_uncalib'], 
        y=mag_df['y_uncalib'],
        name = 'xy')
    )
    fig.add_trace(go.Scatter(
        x=mag_df['x_uncalib'], 
        y=mag_df['z_uncalib'],
        name = 'xz')
    )
    fig.add_trace(go.Scatter(
        x=mag_df['y_uncalib'], 
        y=mag_df['z_uncalib'],
        name = 'yz')
    )
    fig.update_layout(
        title= title,
        width = 800,
        height = 800,
        yaxis = dict(
        scaleanchor = "x",
        scaleratio = 1,
        )
    )
    return fig