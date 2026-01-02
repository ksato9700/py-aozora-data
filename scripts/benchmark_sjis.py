import os
import sys
import time

# ruff: noqa: RUF001, RUF003

# Ensure we can import from the source directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aozora_data.sjis_to_utf8 import converter


def benchmark(n: int = 1000):
    """Benchmark the converter performance."""
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
        converter.convert_content_py(sample_bytes)
    py_time = time.time() - start
    print(f"Python implementation: {py_time:.4f} seconds")

    # Benchmark Rust version
    if hasattr(converter, "convert_content_rs") and converter.convert_content_rs:
        start = time.time()
        for _ in range(n):
            converter.convert_content_rs(sample_bytes)
        rs_time = time.time() - start
        print(f"Rust implementation:   {rs_time:.4f} seconds")
        print(f"Speedup: {py_time / rs_time:.2f}x")

        # Verify correctness
        assert converter.convert_content_py(sample_bytes) == converter.convert_content_rs(
            sample_bytes
        )
        print("Verification: Outputs match.")
    else:
        print("Rust implementation not available.")


if __name__ == "__main__":
    benchmark()
