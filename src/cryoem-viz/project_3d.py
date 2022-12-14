#!/usr/bin/env python3

import os
import glob
import mrcfile
import argparse
import numpy as np
import matplotlib.pyplot as plt


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i',
        '--input',
        help="Provide the path to the input mrc file(s). Can be a wildcard.")
    ap.add_argument('-o',
                    '--odir',
                    help='Provide the path to the output directory.')
    ap.add_argument('--skipdone',
                    default=False,
                    action="store_true",
                    help='Skip the files already converted.')
    args = vars(ap.parse_args())
    return args


def is_mrc(filename):
    return filename.endswith(('.mrc'))


def is_done(filename, odir):
    oname = os.path.splitext(os.path.basename(filename))[0] + '.png'
    return oname in os.listdir(odir)


def project_3d(mrc, odir):
    a = mrcfile.open(mrc, permissive=True).data
    x = np.sum(a, axis=0)
    y = np.sum(a, axis=1)
    z = np.sum(a, axis=2)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True)
    ax1.imshow(x, cmap='gray')
    ax2.imshow(y, cmap='gray')
    ax3.imshow(z, cmap='gray')

    oname = os.path.basename(mrc).split('.')[0] + '.png'
    fig.set_figheight(3)
    fig.set_figwidth(9)
    fig.savefig(os.path.join(odir, oname))


def main(**args):
    for f in glob.glob(args['input']):
        if is_mrc(f):
            if args['skipdone'] and is_done(f, args['odir']):
                pass
            else:
                project_3d(f, args['odir'])


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)
