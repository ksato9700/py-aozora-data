import argparse
import sys

from .converter import TextToXhtmlConverter


def main():
    """Convert Aozora Bunko text to XHTML."""
    parser = argparse.ArgumentParser(description="Convert Aozora Bunko text to XHTML.")
    parser.add_argument("input", help="Path to input text file (UTF-8)")
    parser.add_argument("output", help="Path to output XHTML file")

    args = parser.parse_args()

    try:
        converter = TextToXhtmlConverter(args.input, args.output)
        converter.convert()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
