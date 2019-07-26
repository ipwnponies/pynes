import argparse  # pragma: no cover


def argparser() -> argparse.ArgumentParser:  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=argparse.FileType('rb'))
    return parser


def main() -> None:  # pragma: no cover
    parser = argparser()
    parser.parse_args()


if __name__ == '__main__':
    main()
