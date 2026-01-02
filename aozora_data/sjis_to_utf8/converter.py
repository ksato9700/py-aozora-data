"""Converter module for Shift JIS to UTF-8 with Gaiji support."""

import os
import re

# Global cache for the Gaiji table
GAIJI_TABLE: dict[str, str] = {}


def load_gaiji_table(table_path: str = "jisx0213-2004-std.txt") -> None:
    """Load the JIS X 0213 to Unicode mapping table."""
    global GAIJI_TABLE
    if GAIJI_TABLE:
        return

    # Try finding the file in a few locations:
    # 1. Specified path (relative to CWD)
    # 2. Same directory as this module (if bundled)
    # 3. Project root (common dev setup)

    candidates = [
        table_path,
        os.path.join(os.path.dirname(__file__), table_path),
        # Up one level (aozora_data/sjis_to_utf8 -> aozora_data)
        os.path.join(os.path.dirname(os.path.dirname(__file__)), table_path),
        # Up two levels (aozora_data -> root) to find file in repo root
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), table_path),
    ]

    found_path = None
    for p in candidates:
        if os.path.exists(p):
            found_path = p
            break

    if not found_path:
        # If not found, we can't perform replacement.
        # For now, we'll just return and sub_gaiji will fail to replace (return original).
        # Or should we warn?
        return

    with open(found_path, encoding="utf-8", errors="ignore") as f:
        # Parse lines like: 3-2121	U+3000	# IDEOGRAPHIC SPACE
        # Regex adapted from user snippet: (\d-\w{4})\s+U\+(\w{4})
        ms = (re.match(r"(\d-\w{4})\s+U\+(\w{4})", lst) for lst in f if lst and lst[0] != "#")
        GAIJI_TABLE.update({m[1]: chr(int(m[2], 16)) for m in ms if m})


def get_gaiji(s: str) -> str:
    """Resolve an Aozora Bunko Gaiji annotation string to a Unicode character.

    Examples:
        ※［＃「弓＋椁のつくり」、第3水準1-84-22］
        ※［＃「身＋單」、U+8EC3、56-1］

    """  # noqa: RUF002
    # Ensure table is loaded
    if not GAIJI_TABLE:
        load_gaiji_table()

    # Pattern 1: JIS X 0213 plane/row/cell
    # e.g., 第3水準1-84-22 -> plane=1, row=84, cell=22 (in user snippet logic context?)
    # User snippet: m = re.search(r'第(\d)水準\d-(\d{1,2})-(\d{1,2})', s)
    # key = f'{m[1]}-{int(m[2])+32:2X}{int(m[3])+32:2X}'
    # This logic constructs the key format found in the table (e.g., 3-XXXX).
    # Wait, the table keys are like "3-2121".
    # 3-2121 corresponds to: Plane 1 (of JIS X 0213), Row 1, Cell 1 ? No.
    # JIS X 0213 Plane 1 is mapped to prefix "3-" in the file provided?
    # File header says:
    # 3-XXXX	JIS X 0213:2004 plane 1 (GL encoding)
    # 4-XXXX	JIS X 0213:2000 plane 2 (GL encoding)
    # The user snippet logic: key = f'{m[1]}-{int(m[2])+32:2X}{int(m[3])+32:2X}'
    # m[1] is the plane number from "第(N)水準".
    # Actually "第3水準" usually refers to JIS X 0213 Plane 1. "第4水準" is Plane 2.
    # The snippet takes m[1] (which creates '3' or '4').
    # Then takes row and cell, adds 32 (0x20) to convert to GL encoding byte values?
    # Example: 1-84-22. 84+32=116 (0x74). 22+32=54 (0x36). Key: "3-7436" if m[1]=3.

    m = re.search(r"第(\d)水準\d-(\d{1,2})-(\d{1,2})", s)
    if m:
        # m[1] is likely 3 or 4.
        # table keys format: "3-XXXX" where XXXX is hex bytes.
        key = f"{m[1]}-{int(m[2]) + 32:2X}{int(m[3]) + 32:2X}"
        return GAIJI_TABLE.get(key, s)

    # Pattern 2: Direct Unicode Reference
    # e.g., U+8EC3
    m = re.search(r"U\+(\w{4})", s)
    if m:
        return chr(int(m[1], 16))

    # Return original string if no match found
    return s


def sub_gaiji(text: str) -> str:
    """Replace Aozora Bunko Gaiji annotations in the text."""
    # Regex for annotation: ※［＃.+?］ # noqa: RUF003
    return re.sub(r"※［＃.+?］", lambda m: get_gaiji(m.group(0)), text)  # noqa: RUF001


def convert_content(content: bytes) -> str:
    """Decode Shift JIS (JIS X 0208) bytes to a UTF-8 string and replaces Aozora Bunko Gaiji.

    Args:
        content: The bytes content encoded in Shift JIS.

    Returns:
        The decoded string (Unicode) with Gaiji replaced.

    """
    # Using 'shift_jis' strictly as per Aozora Bunko specifications.
    text = content.decode("shift_jis")
    return sub_gaiji(text)


def convert_file(src_path: str, dest_path: str) -> None:
    """Read a Shift JIS file and saves it as a UTF-8 file with Gaiji replacement.

    Args:
        src_path: Path to the source file (Shift JIS).
        dest_path: Path to the destination file (will be UTF-8).

    """
    with open(src_path, "rb") as f:
        content = f.read()

    decoded_content = convert_content(content)

    # Write as UTF-8
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(decoded_content)
