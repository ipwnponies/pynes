import argparse


def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=argparse.FileType('rb'))
    return parser


def main() -> None:
    parser = argparser()
    parser.parse_args()


if __name__ == '__main__':
    main()
