#!/usr/bin/env python
"""Resize the image to given size.

Don't strech images, crop and center instead.

Courtesy of ZED on https://gist.github.com/zed/4221180>



Check on: http://pillow.readthedocs.org/en/latest/reference/ImageFilter.html



"""
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from fractions import Fraction
from functools import partial
from multiprocessing import Pool

from PIL import Image # $ sudo apt-get install python-imaging

def crop_resize(image, size, ratio):
    # crop to ratio, center
    w, h = image.size
    if w > ratio * h: # width is larger then necessary
        x, y = (w - ratio * h) // 2, 0
    else: # ratio*height >= width (height is larger)
        x, y = 0, (h - w / ratio) // 2
    image = image.crop((x, y, w - x, h - y))

    # resize
    if image.size > size: # don't stretch smaller images
        image.thumbnail(size, Image.ANTIALIAS)
    return image

def crop_resize_mp(input_filename, outputdir, size, ratio):
    try:
        image = crop_resize(Image.open(input_filename), size, ratio)

        # save resized image
        basename, ext = os.path.splitext(os.path.basename(input_filename))
        output_basename = basename + "_thumb" + ext
        output_filename = os.path.join(outputdir, output_basename)
        image.save(output_filename)

        return (input_filename, output_filename), None
    except Exception as e:
        return (input_filename, None), e

def main():
    # parse command-line arguments
    parser = ArgumentParser(description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--size', type=int, nargs=2,
                        default=[800, 250], metavar='N',
                        help='new image size (default 800x250)')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('--outputdir', default=os.curdir, metavar='DIR',
                        help='directory where to save resized images')
    parser.add_argument('files', nargs='+',
                        help='image filenames to process')
    args = parser.parse_args()

    # crop, resize using multiple processes
    error_count = 0
    f = partial(crop_resize_mp, outputdir=args.outputdir, size=args.size,
                ratio=Fraction(*args.size))
    pool = Pool() # use all available cpus
    for (infile, outfile), error in pool.imap_unordered(f, args.files):
        if error is not None:
            error_count += 1
            sys.stderr.write("error: %s: %s\n" % (infile, error))
        elif not args.quiet:
            print("%s -> %s" % (infile, outfile))
    sys.exit(error_count != 0)

if __name__ == "__main__":
    main()
