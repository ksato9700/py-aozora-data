import argparse
import os
import sys
import time

# ruff: noqa: RUF001, RUF003

# Ensure we can import from the source directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aozora_data.sjis_to_utf8 import converter


def benchmark(n: int = 1000, file_path: str | None = None):
    """Benchmark the converter performance."""
    if file_path:
        with open(file_path, "rb") as f:
            sample_bytes = f.read()
        print(f"Loaded {file_path}")
    else:
        # Create a dummy Shift JIS content with some Gaiji
        # "こんにちは" + Gaiji + "さようなら" * repeated
        # Gaiji: ※［＃「弓＋椁のつくり」、第3水準1-84-22］ -> U+5F34 (弴)

        sample_text = "こんにちは" + "※［＃「弓＋椁のつくり」、第3水準1-84-22］" + "さようなら"
        sample_bytes = sample_text.encode("shift_jis") * 100

    print(f"Sample size: {len(sample_bytes)} bytes")
    print(f"Running {n} iterations...")

    # Benchmark Python version
    start = time.time()
    for _ in range(n):
        converter.convert_content(sample_bytes)
    py_time = time.time() - start
    print(f"Memory Conversion: {py_time:.4f} seconds")

    print("-" * 20)

    # Benchmark File I/O + Conversion
    if file_path:
        print(f"Running {n} iterations (Full File I/O)...")
        import tempfile

        start = time.time()
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_path = tmp.name
            for _ in range(n):
                converter.convert_file(file_path, tmp_path)
        py_io_time = time.time() - start
        print(f"File Conversion:   {py_io_time:.4f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark SJIS conversion")
    parser.add_argument("file_path", nargs="?", help="Path to the file to benchmark")
    parser.add_argument("-n", type=int, default=1000, help="Number of iterations")
    args = parser.parse_args()

    benchmark(n=args.n, file_path=args.file_path)
