#!/usr/bin/env python3
'''
INPUT: mrc and star file (coords) with the same file name.
OUTPUT: html. Save in odir.
'''

import numpy as np
import starfile
import mrcfile
import pandas as pd
import argparse
import plotly.express as px
import plotly.graph_objects as go

from utils.utils import downsample


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the path to the input mrc file.")
    ap.add_argument('--star',
                    help="Provide the path to the input star coordinate file.")
    ap.add_argument(
        '--oname',
        default=None,
        help=
        "Provide the name of the output html. Default is the basename of input file with prefix ls-."
    )
    ap.add_argument(
        '-o',
        '--odir',
        default=None,
        help=
        'Provide the path to the output directory. Default is current directory.'
    )
    ap.add_argument('--height',
                    default=600,
                    help="Height of the scaled image. Default is 600.")
    ap.add_argument(
        '--binnum',
        default=20,
        help="Number of bins for the merit slide bar. Default is 20.")

    args = vars(ap.parse_args())
    return args


def main(**args):
    df = starfile.read(args['star'])
    img = mrcfile.read(args['input'])
    bin_num = args['binnum']

    img_h = args['height']
    factor = img_h / img.shape[0]
    img_w = int(img.shape[1] * factor)
    img = downsample(img, img_h)

    a = df['rlnAutopickFigureOfMerit'].to_numpy()
    if (a[0] == a).all():
        bin_num = 1

    out, bins = pd.cut(df["rlnAutopickFigureOfMerit"], bin_num, retbins=True)
    dfs = tuple(df.groupby(out))

    # BELOW: plot overlay
    fig = px.imshow(img, binary_string=True)

    i = 1
    for df in dfs:
        df = df[1]
        fig.add_trace(
            go.Scatter(
                x=df['rlnCoordinateX'] * factor,
                y=df['rlnCoordinateY'] * factor,
                mode='markers',
                marker=dict(
                    symbol='circle-open',
                    size=5,
                    color='red',
                    opacity=i / bin_num,
                    showscale=False,
                ),
                text=[
                    '{:0.3f}'.format(i) for i in df['rlnAutopickFigureOfMerit']
                ],
                hovertemplate='<i>Merit</i>: %{text}',
                name="",
                showlegend=False,
            ))
        i += 1

    merit_steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[
                {
                    "visible":
                    [True] + [False] * i + [True] * (len(fig.data) - 1 - i)
                },
            ],
            label="{:0.3f}".format(bins[i]),
        )
        merit_steps.append(step)

    marker_steps = []
    for i in range(2, 40, 2):
        step = dict(
            method="restyle",
            args=[
                {
                    "marker.size": i
                },
            ],
            label="{:0.3f}".format(i / factor),
        )
        marker_steps.append(step)

    sliders = [
        dict(
            active=0,
            currentvalue={"prefix": "Threshold: "},
            steps=merit_steps,
            pad={
                "l": 10,
                "t": 0
            },
        ),
        dict(
            active=5,
            currentvalue={"prefix": "Marker size (px): "},
            steps=marker_steps,
            pad={
                "l": 10,
                "t": 100
            },
        ),
    ]

    fig.update_layout(
        sliders=sliders,
        width=img_w,
        height=img_h,
        margin={
            "l": 0,
            "r": 0,
            "t": 0,
            "b": 0
        },
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # fig.show(config={'responsive': False})
    # BELOW: save as html
    if args['oname'] is None:
        oname = 'ls-' + os.path.splitext(os.path.basename(
            args[input]))[0] + '.html'
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
