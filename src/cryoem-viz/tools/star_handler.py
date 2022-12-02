#!/usr/bin/env python3
'''
Similar to relion star handler, operate on star file.
'''

import starfile
import argparse


def setupParserOptions():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i',
                    '--input',
                    help="Provide the path to the input star file.")
    ap.add_argument('-o',
                    '--output',
                    help='Provide the path/name of the output star file.')
    ap.add_argument('--blockheader',
                    default=None,
                    help='Provide the block header you want to operate on.\
                         Default is None.')
    ap.add_argument('--key',
                    default=None,
                    help='Provide the block header you want to operate on.\
                         Default is None.')
    ap.add_argument('--select',
                    default=False,
                    action="store_true",
                    help='Select entries that matches the criteria.')
    ap.add_argument('--equals_to',
                    default=None,
                    type=str,
                    help='Select entries that equals to the given parameter.\
                         Can be a str, num or list seperated by comma\
                             (e.g.: 1,2).')
    ap.add_argument(
        '--smaller_than',
        type=float,
        default=None,
        help='Select entries that smaller than the given parameter.\
                         Can be a num.')
    ap.add_argument('--bigger_than',
                    default=None,
                    type=float,
                    help='Select entries that bigger than the given parameter.\
                         Can be a num.')
    ap.add_argument('--subset',
                    default=1.0,
                    help='Take a subset (0 to 1) of the samples.\
                         Default is 1, which uses all samples in the file.')
    args = vars(ap.parse_args())
    return args


def readstarfile(input, blockheader, subset):
    df = starfile.read(input)
    if blockheader is not None:
        df = df[blockheader]
    if subset < 1.0:
        df = df.sample(frac=subset)
    return df


def select(df, key, equals_to, smaller_than, bigger_than):
    if smaller_than is not None:
        df = df[df[key] < smaller_than]
    if bigger_than is not None:
        df = df[df[key] > bigger_than]
    if equals_to is not None:
        try:
            e = float(equals_to)  # if equals to is a number
            df = df[df[key] == e]
        except ValueError:
            e_list = [e.strip() for e in equals_to.split(',')]
            df = df[df[key].astype(str).isin(e_list)]
    return df


def writestarfile(df, input, blockheader, output):
    old_df = starfile.read(input)
    if blockheader is not None:
        old_df[blockheader] = df
    else:
        old_df = df
    starfile.write(old_df, output, overwrite=True)


def main(**args):
    df = readstarfile(args['input'], args['blockheader'], args['subset'])
    if args['select']:
        df = select(df, args['key'], args['equals_to'], args['smaller_than'],
                    args['bigger_than'])
    writestarfile(df, args['input'], args['blockheader'], args['output'])


if __name__ == '__main__':
    args = setupParserOptions()
    main(**args)
