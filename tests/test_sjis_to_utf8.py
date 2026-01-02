from pathlib import Path

from aozora_data.sjis_to_utf8 import convert_content, convert_file


def test_convert_content_basic():
    # "こんにちは" in Shift JIS
    sjis_content = b"\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd"
    expected = "こんにちは"
    assert convert_content(sjis_content) == expected


def test_convert_content_ascii():
    sjis_content = b"Hello World"
    expected = "Hello World"
    assert convert_content(sjis_content) == expected


def test_convert_file(tmp_path: Path):
    src_file = tmp_path / "test_sjis.txt"
    dest_file = tmp_path / "test_utf8.txt"

    # "青空文庫" in Shift JIS
    content = b"\x90\xc2\x8b\xf3\x95\xb6\x8c\xc9"
    src_file.write_bytes(content)

    convert_file(str(src_file), str(dest_file))

    assert dest_file.exists()
    assert dest_file.read_text(encoding="utf-8") == "青空文庫"


def test_cp932_specific_chars_fail():
    # Windows extension "①" (0x8740 in CP932)
    # Rust encoding_rs supports CP932 (SHIFT_JIS standard in web), so this will pass.
    # Python's 'shift_jis' codec is strict JIS X 0208 and fails.
    cp932_char = b"\x87\x40"

    # If using Rust, it decodes to ①. If Python, it raises.
    try:
        res = convert_content(cp932_char)
        # If we reached here, it must be the Rust implementation (or we switched Python to cp932)
        assert res == "①"
    except UnicodeDecodeError:
        # Python implementation behavior
        pass


def test_gaiji_replacement_jis_x_0213():
    # Test replacement of JIS X 0213 reference
    # Annotation: ※［＃「弓＋椁のつくり」、第3水準1-84-22］  # noqa: RUF003
    # Shift JIS encoding of the annotation is tricky to construct manually if it contains kanji.
    # But convert_content takes bytes.
    # The annotation itself is usually written in standard characters (Kanji, Hiragana, etc.)
    # present in Shift JIS.
    # Let's construct a simple byte sequence for the annotation part assuming standard chars.
    # Or easier: construct the string and encode it to shift_jis (Python's shift_jis covers
    # the annotation TEXT).

    # 1-84-22 (Plane 1, Row 84, Cell 22) -> U+391C (㤜)?
    # Let's check the table using grep/find logic or just trust the logic.
    # In jisx0213-2004-std.txt:
    # 3-7436	U+391C	#
    # 84+32 = 116 = 0x74
    # 22+32 = 54  = 0x36
    # So 3-7436 is indeed 1-84-22.
    # U+391C is 㤜.

    annotation = "※［＃「弓＋椁のつくり」、第3水準1-84-22］"  # noqa: RUF001
    # Encode annotation to Shift JIS
    input_bytes = annotation.encode("shift_jis")

    # Expected: The annotation is replaced by U+5F34 (弴) according to jisx0213-2004-std.txt
    expected = "\u5f34"

    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_unicode():
    # Test replacement of direct Unicode reference
    # Annotation: ※［＃「身＋單」、U+8EC3、56-1］ # noqa: RUF003
    # U+8EC3 is 軃

    annotation = "※［＃「身＋單」、U+8EC3、56-1］"  # noqa: RUF001
    input_bytes = annotation.encode("shift_jis")

    expected = "\u8ec3"

    assert convert_content(input_bytes) == expected


def test_gaiji_mixed_content():
    # Mixed content with text and gaiji
    # "文字" + Gaiji + "文字"
    text = "前※［＃「弓＋椁のつくり」、第3水準1-84-22］後"  # noqa: RUF001
    input_bytes = text.encode("shift_jis")

    expected = "前\u5f34後"

    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_plane2():
    # ※［＃「插」でつくりの縦棒が下に突き抜けている、第4水準2-13-28］ # noqa: RUF003
    # 第4水準 -> Plane 2 -> Prefix 4-
    # 2-13-28 -> Row 13, Cell 28
    # 13 + 32 = 45 (0x2D)
    # 28 + 32 = 60 (0x3C)
    # Key: 4-2D3C
    # Mapped to U+63F7 in jisx0213-2004-std.txt

    annotation = "※［＃「插」でつくりの縦棒が下に突き抜けている、第4水準2-13-28］"  # noqa: RUF001
    input_bytes = annotation.encode("shift_jis")

    expected = "\u63f7"

    assert convert_content(input_bytes) == expected
