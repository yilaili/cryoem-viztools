import os
import starfile
import argparse
import plotly.graph_objects as go
from scipy.spatial.transform import Rotation as R
import numpy as np


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the path to the input star file.")
    ap.add_argument('--oname',
                    default=None,
                    help="Provide the name of the output html.\
             Default is the basename of input file with plot type.")
    ap.add_argument('-o',
                    '--odir',
                    default=None,
                    help='Provide the path to the output directory.')
    ap.add_argument('-s',
                    '--size',
                    default=2,
                    help='Marker size for plotting.')

    args = vars(ap.parse_args())
    return args


def readstarfile(input):
    df = starfile.read(input)
    return df['particles'].select_dtypes(include='number')


def prep_sphere(r=0.99):
    u = np.linspace(0, 2 * np.pi, 120)
    v = np.linspace(0, np.pi, 60)
    X = r * np.outer(np.cos(u), np.sin(v))
    Y = r * np.outer(np.sin(u), np.sin(v))
    Z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    return (X, Y, Z)


def prep_particles(df):
    v_0 = np.array([[0., 1., 0.]])
    xyz_0 = np.tile(v_0, len(df)).reshape(-1, 3)

    rots = np.stack([
        df['rlnAngleRot'].values, df['rlnAngleTilt'].values,
        df['rlnAnglePsi'].values
    ],
                    axis=1)
    r = R.from_euler('zyz', rots, degrees=True)
    xyz = r.apply(xyz_0)
    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]
    return (x, y, z)


def plot(df, x, y, z, X, Y, Z, marker_size):
    fig = go.Figure()

    for c in df.columns:
        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode='markers',
                visible=False,
                marker=dict(
                    color=df[c],
                    colorscale='Viridis',
                    size=marker_size,
                    showscale=True,
                    opacity=0.8,
                ),
                text=['{:0.3f}'.format(i) for i in df[c]],
                hovertemplate=c + ': %{text}',
                name='',
            ))

    fig.data[0].visible = True

    fig.add_trace(
        go.Surface(x=X,
                   y=Y,
                   z=Z,
                   opacity=0.1,
                   cmax=0.4,
                   cmin=0.4,
                   colorscale='Greys',
                   showscale=False,
                   hoverinfo='skip',
                   name=''))

    button_layer_1_height = 1.10

    buttons = []
    for i in range(len(fig.data) - 1):
        button = dict(method="update",
                      args=[{
                          "visible": [False] * len(fig.data) + [True]
                      }],
                      label=df.columns[i])
        button["args"][0]["visible"][i] = True
        buttons.append(button)

    updatemenus = [
        dict(buttons=buttons,
             direction="down",
             pad={
                 "r": 10,
                 "t": 10
             },
             showactive=True,
             x=0.1,
             xanchor="left",
             y=button_layer_1_height,
             yanchor="top")
    ]

    fig.update_layout(scene={
        "aspectratio": {
            "x": 1,
            "y": 1,
            "z": 0.5
        },
        "xaxis": {
            'showbackground': False,
            'visible': False
        },
        "yaxis": {
            'showbackground': False,
            'visible': False
        },
        "zaxis": {
            "range": [0, 1],
            'showbackground': False,
            'visible': False
        }
    },
                      height=500,
                      width=800,
                      autosize=False,
                      margin=dict(r=20, l=20, b=10, t=10),
                      updatemenus=updatemenus,
                      annotations=[
                          dict(text="Color:",
                               x=0,
                               xref="paper",
                               y=1.06,
                               yref="paper",
                               align="left",
                               showarrow=False)
                      ])

    return fig


def main(**args):
    df = readstarfile(args['input'])
    X, Y, Z = prep_sphere(r=0.99)
    x, y, z = prep_particles(df)

    fig = plot(df, x=x, y=y, z=z, X=X, Y=Y, Z=Z, marker_size=args['size'])

    if args['oname'] is None:
        oname = os.path.splitext(os.path.basename(
            args['input']))[0] + '-orientation.html'
    else:
        oname = args['oname']
    if args['odir'] is None:
        odir = './'
    else:
        odir = args['odir']

    fig.write_html(os.path.join(odir, oname))


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)
