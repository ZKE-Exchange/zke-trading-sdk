import argparse
from .installer import install


def main():
    parser = argparse.ArgumentParser(prog="zke")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install")

    args = parser.parse_args()

    if args.command == "install":
        install()
    else:
        parser.print_help()
