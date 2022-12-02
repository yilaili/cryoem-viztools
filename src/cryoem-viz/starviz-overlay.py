import starfile
import mrcfile
import os
import plotly.express as px
import plotly.graph_objects as go
from utils.utils import downsample
import argparse


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the path to the input star file.")
    ap.add_argument('-o',
                    '--odir',
                    default=None,
                    help='Provide the path to the output directory.\
             Default is current directory.')
    ap.add_argument('--height',
                    default=600,
                    help="Height of the scaled image. Default is 600.")
    ap.add_argument('--subset',
                    default=1.0,
                    help='Take a subset (0 to 1) of the particles.\
                         Default is 1, which uses the full dataset.')

    args = vars(ap.parse_args())
    return args


def readstarfile(input, subset):
    df = starfile.read(input)['particles']
    if subset < 1.0:
        df = df.sample(frac=subset).select_dtypes(include='number')
    return df


def starviz_overlay(df, img, img_h):

    factor = img_h / img.shape[0]
    img = downsample(img, img_h)

    fig = px.imshow(img, binary_string=True)

    for z in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['rlnCoordinateX'] * factor,
                y=df['rlnCoordinateX'] * factor,
                mode='markers',
                visible=False,
                marker=dict(color=df[z],
                            colorscale='Viridis',
                            size=5,
                            showscale=True),
                name='',
            ))

    fig.data[0].visible = True

    button_layer_1_height = 1.10

    buttons = []
    for i in range(len(fig.data)):
        button = dict(method="update",
                      args=[{
                          "visible": [True] + [False] * len(fig.data)
                      }],
                      label=df.columns[i + 1])
        button["args"][0]["visible"][i + 1] = True
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
             yanchor="top"),
    ]

    fig.update_layout(
        xaxis_title='rlnCoordinateX',
        yaxis_title='rlnCoordinateY',
        #   width=700,
        height=700,
        autosize=False,
        margin=dict(t=50, b=0, l=0, r=0),
        updatemenus=updatemenus,
        annotations=[
            dict(text="Color",
                 x=0,
                 xref="paper",
                 y=1.07,
                 yref="paper",
                 align="left",
                 showarrow=False)
        ])

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    return fig


def main(**args):
    if args['odir'] is None:
        odir = './'
    else:
        odir = args['odir']

    img_h = args['height']

    df = readstarfile(args['input'], args['subset'])
    dfs = df.groupby('rlnMicrographName')

    for mic, df_temp in dfs:
        img = mrcfile.read(mic)
        img = downsample(img, img_h)
        oname = 'ls-' + os.path.basename(mic).split('.')[0] + '-overlay.html'
        fig = starviz_overlay(df_temp, img, img_h)
        fig.write_html(os.path.join(odir, oname))


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)
