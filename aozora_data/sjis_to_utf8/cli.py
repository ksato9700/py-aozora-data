"""CLI tool for sjis_to_utf8."""

import argparse
import os
import sys

from .converter import convert_file


def main() -> None:
    """Convert Aozora Bunko Shift JIS file to UTF-8 with Gaiji replacement."""
    parser = argparse.ArgumentParser(
        description="Convert Aozora Bunko Shift JIS file to UTF-8 with Gaiji replacement."
    )
    parser.add_argument("input", help="Input file path (Shift JIS)")
    parser.add_argument("output", help="Output file path (UTF-8)")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        convert_file(args.input, args.output)
        print(f"Successfully converted '{args.input}' to '{args.output}'")
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
