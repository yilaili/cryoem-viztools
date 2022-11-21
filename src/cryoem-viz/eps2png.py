#!/usr/bin/env python3

import os
import glob
import argparse
from PIL import Image


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i',
        '--input',
        help="Provide the path to the input eps file(s). Can be a wildcard.")
    ap.add_argument('-o',
                    '--odir',
                    help='Provide the path to the output directory.')
    ap.add_argument('--skipdone',
                    default=False,
                    action="store_true",
                    help='Skip the files already converted.')
    args = vars(ap.parse_args())
    return args


def is_eps(filename):
    return filename.endswith(('.eps'))


def is_done(filename, odir):
    oname = os.path.splitext(os.path.basename(filename))[0] + '.png'
    return oname in os.listdir(odir)


def eps2png(img_eps, odir):
    im = Image.open(img_eps)
    fig = im.convert('RGBA')
    oname = img_eps[:-4] + '.png'
    fig.save(os.path.join(odir, oname), lossless=True)


def main(**args):
    for f in glob.glob(args['input']):
        if is_eps(f):
            if args['skipdone'] and is_done(f, args['odir']):
                pass
            else:
                eps2png(f, args['odir'])


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)
