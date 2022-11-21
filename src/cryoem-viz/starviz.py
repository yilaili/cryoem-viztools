import os
import starfile
import argparse
import plotly.graph_objects as go


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the path to the input star file.")
    ap.add_argument(
        '--oname',
        default=None,
        help="Provide the name of the output html.\
             Default is the basename of input file with plot type."
    )
    ap.add_argument('-o',
                    '--odir',
                    default=None,
                    help='Provide the path to the output directory.')
    ap.add_argument(
        '-t',
        '--type',
        help='Type of the star file.\
             Support `micrograph` and `particles` for now.')
    ap.add_argument(
        '--plot',
        help='Type of the plot. Support `scatter` and `histogram` for now.')
    ap.add_argument('--plotx',
                    help='x axis for scatter plot. e.g. rlnCoordinateX')
    ap.add_argument('--ploty',
                    help='y axis for scatter plot. e.g. rlnCoordinateY')
    args = vars(ap.parse_args())
    return args


def readstarfile(input, type):
    df = starfile.read(input)
    if type == 'micrographs':
        return df['micrographs'].select_dtypes(include='number')
    if type == 'particles':
        return df['particles'].select_dtypes(include='number')


def plot_scatter(df, plot_x, plot_y):
    fig = go.Figure()

    for z in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df[plot_x],
                y=df[plot_y],
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
                          "visible": [False] * len(fig.data)
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
             yanchor="top"),
    ]

    fig.update_layout(xaxis_title=plot_x,
                      yaxis_title=plot_y,
                      width=700,
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

    return fig


def plot_histogram(df):
    fig = go.Figure()

    for z in df.columns:
        fig.add_trace(
            go.Histogram(
                x=df[z],
                name='',
                showlegend=False,
                visible=False,
            ))

    fig.data[0].visible = True

    button_layer_1_height = 1.18

    buttons = []
    for i in range(len(fig.data)):
        button = dict(method="update",
                      args=[{
                          "visible": [False] * len(fig.data)
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
             x=0.12,
             xanchor="left",
             y=button_layer_1_height,
             yanchor="top"),
    ]

    fig.update_layout(width=700,
                      height=400,
                      autosize=False,
                      margin=dict(t=50, b=0, l=0, r=0),
                      updatemenus=updatemenus,
                      annotations=[
                          dict(text="Histogram: ",
                               x=0,
                               xref="paper",
                               y=1.12,
                               yref="paper",
                               align="left",
                               showarrow=False)
                      ])

    return fig


def main(**args):
    df = readstarfile(args['input'], args['type'])
    if args['plot'] == 'scatter':
        fig = plot_scatter(df, args['plotx'], args['ploty'])
    elif args['plot'] == 'histogram':
        fig = plot_histogram(df)

    if args['oname'] is None:
        oname = os.path.splitext(os.path.basename(
            args['input']))[0] + '-' + args['plot'] + '.html'
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
