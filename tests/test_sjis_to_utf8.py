from pathlib import Path

from aozora_data.sjis_to_utf8 import convert_content, convert_file

# ruff: noqa: RUF001, RUF003, E501


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
    # Python's 'shift_jis_2004' codec supports both JIS X 0213 and common extensions.
    cp932_char = b"\x87\x40"

    # Assuming shift_jis_2004 decodes it correctly as ①
    res = convert_content(cp932_char)
    assert res == "①"


def test_gaiji_replacement_jis_x_0213():
    # Test replacement of JIS X 0213 reference
    # Annotation: ※［＃「弓＋椁のつくり」、第3水準1-84-22］
    # 1-84-22 (Plane 1, Row 84, Cell 22) -> 3-7436 -> U+5F34 (弴)

    annotation = "※［＃「弓＋椁のつくり」、第3水準1-84-22］"
    # Encode annotation to Shift JIS 2004
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "\u5f34"

    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_unicode():
    # Test replacement of direct Unicode reference
    # Annotation: ※［＃「身＋單」、U+8EC3、56-1］
    # U+8EC3 is 軃

    annotation = "※［＃「身＋單」、U+8EC3、56-1］"
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "\u8ec3"

    assert convert_content(input_bytes) == expected


def test_gaiji_mixed_content():
    # Mixed content with text and gaiji
    # "文字" + Gaiji + "文字"
    text = "前※［＃「弓＋椁のつくり」、第3水準1-84-22］後"
    input_bytes = text.encode("shift_jis_2004")

    expected = "前\u5f34後"

    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_plane2():
    # ※［＃「插」でつくりの縦棒が下に突き抜けている、第4水準2-13-28］
    # Key: 4-2D3C -> U+63F7
    annotation = "※［＃「插」でつくりの縦棒が下に突き抜けている、第4水準2-13-28］"
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "\u63f7"

    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_fullwidth():
    # Test replacement with full-width numbers (e.g., 第４水準)
    # ※［＃「插」でつくりの縦棒が下に突き抜けている、第４水準2-13-28］
    annotation = "※［＃「插」でつくりの縦棒が下に突き抜けている、第４水準2-13-28］"
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "\u63f7"
    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_large_codepoint():
    # Test replacement of a 5-digit Unicode character
    # 第4水準2-12-11 -> U+2231E (𢌞)

    annotation = "※［＃「廻」の「廴」に代えて「己」、第4水準2-12-11］"
    input_bytes = annotation.encode("shift_jis_2004")

    # 𢌞 (U+2231E)
    expected = "\U0002231e"
    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_generic_pattern():
    # Test generic JIS X 0213 pattern (e.g., "※［＃全角メートル、1-13-35］")
    # 1-13-35 -> Key 3-2D43 -> ㍍ (U+334D)
    annotation = "※［＃全角メートル、1-13-35］"
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "㍍"
    assert convert_content(input_bytes) == expected


def test_gaiji_replacement_without_mark():
    # Test replacement without the standard "※" prefix
    # ［＃「さんずい＋賣」、第3水準1-87-29］ -> 瀆 (U+6FC3)
    # Key 3-773D
    annotation = "［＃「さんずい＋賣」、第3水準1-87-29］"
    input_bytes = annotation.encode("shift_jis_2004")

    expected = "瀆"
    assert convert_content(input_bytes) == expected


def test_gaiji_placeholder():
    # Test replacement of a placeholder character described in the annotation.
    # Case: "1" is a placeholder for "Ⅰ" (Roman Numeral 1, U+2160)
    # Annotation: ［＃「1」はローマ数字、1-13-21］
    # The converter should detect "「1」は..." and replace the preceding "1" with "Ⅰ".

    # "1" (ASCII 0x31) + Annotation
    text = "詩集1［＃「1」はローマ数字、1-13-21］"
    input_bytes = text.encode("shift_jis_2004")

    expected = "詩集Ⅰ"

    assert convert_content(input_bytes) == expected


def test_fullwidth_backslash():
    # Test replacement of Fullwidth Backslash (0x815F)
    # shift_jis_2004 decodes 0x815F to '\\' (U+005C), but Aozora expects '＼' (U+FF3C).
    # We pre-process to preserve it.

    char_sjis = b"\x81\x5f"
    expected = "\uff3c"  # ＼

    assert convert_content(char_sjis) == expected


def test_false_positive_note():
    # Test that a note (not a Gaiji) is left unchanged.
    # Note contains '譃' (U+8B43), which requires shift_jis_2004.
    text = "御側の者たちに眴《めくば》せを［＃「眴《めくば》せを」は底本では「眗《めくば》せを」］なさいました。"
    # Note: Using '眴' (U+7734) as per user report (actually '眴' is ok in jis2004 too?)
    # U+7734 is '眴'. U+8B43 is '譃'.
    # I will verify 譃 as in the latest user claim.

    text = "唐皮《からかは》の花の間《あひだ》に止まれる鸚鵡《あうむ》、（横あひより甲比丹《かぴたん》に）譃《うそ》［＃「譃」は底本では「謔」］ですよ。"
    input_bytes = text.encode("shift_jis_2004")

    # Expected: Original text preserved (Gaiji logic should ignore the note content)
    expected = text
    assert convert_content(input_bytes) == expected


def test_false_positive_placeholder_collision():
    # User report:
    # "御側の者たちに眴《めくば》せを［＃「眴《めくば》せを」は底本では「眗《めくば》せを」］"
    # This matches the placeholder regex "「(.+?)」は", extracting "眴《めくば》せを".
    # And the preceding text ends with "眴《めくば》せを".
    # BUT, this is a note, not a gaiji replacement. get_gaiji returns the annotation as is.
    # Our logic must verify that replacement != annotation before applying placeholder removal.

    text = "御側の者たちに眴《めくば》せを［＃「眴《めくば》せを」は底本では「眗《めくば》せを」］なさいました。"
    input_bytes = text.encode("shift_jis_2004")

    # Expect NO change
    expected = text
    assert convert_content(input_bytes) == expected
