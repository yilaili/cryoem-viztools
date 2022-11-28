import os
import glob
import starfile
import argparse
import plotly.graph_objects as go


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the wildcard path to the\
                         input particle star files.")
    ap.add_argument('--oname',
                    default=None,
                    help="Provide the name of the output html.\
             Default is the basename of input file with plot type.")
    ap.add_argument('-o',
                    '--odir',
                    default=None,
                    help='Provide the path to the output directory.')
    ap.add_argument('--plot',
                    help='Type of the plot. Only support `scatter` for now.')
    ap.add_argument('--plotx',
                    help='x axis for scatter plot. e.g. rlnCoordinateX')
    ap.add_argument('--ploty',
                    help='y axis for scatter plot. e.g. rlnCoordinateY')
    ap.add_argument(
        '--plotz', help='Color map to plot for scatter plot. e.g. rlnAngleRot')
    ap.add_argument('--subset',
                    default=1.0,
                    help='Take a subset (0 to 1) of the particles.\
                         Default is 1, which uses the full dataset.')
    ap.add_argument('--fixedratio',
                    default=True,
                    action="store_true",
                    help='x y ratio is fixed to be 1. Only useful for scatter.\
                         Default is true.')
    args = vars(ap.parse_args())
    return args


def readstarfile(input, subset):
    dfs = []
    for f in sorted(glob.glob(input)):
        df = starfile.read(f)['particles']
        if subset < 1.0:
            df = df.sample(frac=subset)
        dfs.append(df.select_dtypes(include='number'))
    return dfs


def plot_scatter_frames(dfs, plot_x, plot_y, plot_z, fixedratio):

    fig = go.Figure(frames=[
        go.Frame(data=go.Scatter(
            x=df[plot_x],
            y=df[plot_y],
            mode='markers',
            marker=dict(
                color=df[plot_z], colorscale='Viridis', size=5,
                showscale=True),
            text=['{:0.3f}'.format(i) for i in df[plot_z]],
            hovertemplate=plot_z + ': %{text}',
        ),
                 name=str(k)) for k, df in enumerate(dfs)
    ])

    # Add data to be displayed before animation starts
    fig.add_trace(
        go.Scatter(
            x=dfs[0][plot_x],
            y=dfs[0][plot_y],
            mode='markers',
            marker=dict(color=dfs[0][plot_z],
                        colorscale='Viridis',
                        size=5,
                        showscale=True),
            text=['{:0.3f}'.format(i) for i in dfs[0][plot_z]],
            hovertemplate=plot_z + ': %{text}',
            name='',
        ))

    def frame_args(duration):
        return {
            "frame": {
                "duration": duration
            },
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {
                "duration": duration,
                "easing": "linear"
            },
        }

    sliders = [{
        "pad": {
            "b": 10,
            "t": 60
        },
        "len":
        0.9,
        "x":
        0.1,
        "y":
        0,
        "steps": [{
            "args": [[f.name], frame_args(0)],
            "label": str(k),
            "method": "animate",
        } for k, f in enumerate(fig.frames)],
    }]

    # Layout
    fig.update_layout(
        width=600,
        height=600,
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, frame_args(500)],
                    "label": "&#9654;",  # play symbol
                    "method": "animate",
                },
                {
                    "args": [[None], frame_args(0)],
                    "label": "&#9724;",  # pause symbol
                    "method": "animate",
                },
            ],
            "direction":
            "left",
            "pad": {
                "r": 10,
                "t": 70
            },
            "type":
            "buttons",
            "x":
            0.1,
            "y":
            0,
        }],
        sliders=sliders)

    fig.update_layout(
        xaxis_title=plot_x,
        yaxis_title=plot_y,
        #     width=700,
        height=700,
        autosize=False,
        margin=dict(t=50, b=0, l=0, r=0),
        annotations=[
            dict(text="Color: " + plot_z,
                 x=0,
                 xref="paper",
                 y=1.05,
                 yref="paper",
                 align="left",
                 showarrow=False)
        ])

    if fixedratio:
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

    return fig


def main(**args):
    df = readstarfile(args['input'], float(args['subset']))
    if args['plot'] == 'scatter':
        fig = plot_scatter_frames(df, args['plotx'], args['ploty'],
                                  args['plotz'], args['fixedratio'])
    else:
        pass

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
