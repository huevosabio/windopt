from _wavg import *

if __name__ == '__main__':
    
    import argparse
    import logging
    import sys

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger = logging.getLogger('fasterio')

    parser = argparse.ArgumentParser(
        description="Performs weighted averaging of input imagery")
    parser.add_argument(
        'input', 
        metavar='INPUT', 
        nargs='+',
        help="List of input file names")
    parser.add_argument(
        'output', 
        metavar='OUTPUT',
        help="Output file name")
    parser.add_argument(
        '--origin', 
        metavar='Q', 
        type=float, 
        default=20.0, 
        help="Origin of the weighting function. Default: 20.0")
    parser.add_argument(
        '--exponent', 
        metavar='K', 
        type=float, 
        default=1.0, 
        help="Exponent of the weighting function. Default: 1.0")
    args = parser.parse_args()

    filenames = args.input[:~1]
    output_dir = args.input[-1]
    q = args.origin
    k = args.exponent

    print(q, k)

    avg(filenames, output_dir, q, k)

