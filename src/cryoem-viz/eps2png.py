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
    args = vars(ap.parse_args())
    return args


def check_file(filename):
    if filename.endswith(('.eps')):
        return filename
    else:
        return None


def eps2png(img_eps, odir):
    im = Image.open(img_eps)
    fig = im.convert('RGBA')
    oname = img_eps[:-3] + 'png'
    fig.save(os.path.join(odir, oname), lossless=True)


def main(**args):
    os.makedirs('postprocess', exist_ok=True)
    for f in glob.glob(args['input']):
        f = check_file(f)
        if f is not None:
            eps2png(f, args['odir'])


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)