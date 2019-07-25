import argparse


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=argparse.FileType('rb'))
    return parser


def main():
    parser = argparser()
    parser.parse_args()


if __name__ == '__main__':
    main()
