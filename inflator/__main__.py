import argparse
import pprint


def ansi(code):
    return f"\u001b[{code}m"


def main():
    def get_args():
        parser = argparse.ArgumentParser(
            prog="inflate",
            description="Manage libraries for use in goboscript",
            epilog=f'rip "{ansi(31)}-9999 aura 💀{ansi(0)}"'
        )

        parser.add_argument("-i", "--input", action="store", dest="input")

        return parser.parse_args()
    args = get_args()

    print(f"{ansi(31)}HELLO WORLD{ansi(0)}")
    print(args.input)
