import argparse
import sys

from .converter import TextToHtmlConverter


def main():
    """Convert Aozora Bunko text to HTML5."""
    parser = argparse.ArgumentParser(description="Convert Aozora Bunko text to HTML5.")
    parser.add_argument("input", help="Path to input text file (UTF-8)")
    parser.add_argument("output", help="Path to output HTML file")

    args = parser.parse_args()

    try:
        converter = TextToHtmlConverter(args.input, args.output)
        converter.convert()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
