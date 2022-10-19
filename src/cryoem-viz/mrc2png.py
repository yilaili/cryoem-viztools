#!/usr/bin/env python3
'''
Read mrc files, use FFT to downsample them to smaller png files.
The output png files will have height as 494 px and h/w ratio will be kept.
'''

import mrcfile
import os
import glob
import numpy as np
import argparse
from PIL import Image
import multiprocessing as mp


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i',
        '--input',
        help="Provide the path to the input mrc file(s) (can be wildcard).")
    ap.add_argument('-o',
                    '--odir',
                    help='Provide the path to the output directory.')
    ap.add_argument('--height',
                    type=int,
                    default=512,
                    help='Height of the converted png in px. Default is 512.')
    ap.add_argument(
        '--threads',
        type=int,
        default=None,
        help=
        'Number of threads for conversion. Default is None, using mp.cpu_count(). If get memory error, set it to a reasonable number.'
    )
    args = vars(ap.parse_args())
    return args


def downsample(img, height):
    '''
    Downsample 2d array using fourier transform.
    factor is the downsample factor.
    '''
    m, n = img.shape[-2:]
    ds_factor = m / height
    width = round(n / ds_factor / 2) * 2
    F = np.fft.rfft2(img)
    A = F[..., 0:height // 2, 0:width // 2 + 1]
    B = F[..., -height // 2:, 0:width // 2 + 1]
    F = np.concatenate([A, B], axis=0)
    f = np.fft.irfft2(F, s=(height, width))
    return f


def scale_image(img, height):
    newImg = downsample(img, height)
    newImg = ((newImg - newImg.min()) /
              ((newImg.max() - newImg.min()) + 1e-7) * 255)
    newImg = Image.fromarray(newImg).convert('L')
    return newImg


def save_image(mrc_name, odir, height):
    try:
        micrograph = mrcfile.open(mrc_name, permissive=True).data
        micrograph = micrograph.reshape(
            (micrograph.shape[-2], micrograph.shape[-1]))
        newImg = scale_image(micrograph, height)
        newImg.save(
            os.path.join(
                odir,
                os.path.splitext(os.path.basename(mrc_name))[0] + '.png'))
    except ValueError:
        print('An error occured when trying to save ', mrc_name)
        pass


def mrc2png(**args):
    threads = mp.cpu_count() if args['threads'] is None else args['threads']
    with mp.Pool(threads) as pool:
        print('Processing in %d parallel threads....' % threads)
        pool.starmap(save_image, ((mrc_name, args['odir'], args['height'])
                                  for mrc_name in glob.glob(args['input'])))


if __name__ == '__main__':
    args = setupParserOptions()
    if os.path.splitext(args['input'])[1] == '.mrc':
        mrc2png(**args)