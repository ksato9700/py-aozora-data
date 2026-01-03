from aozora_data.sjis_to_utf8 import convert_content

# ruff: noqa: RUF001, RUF003


def test_handakuten_katakana():
    # Input: ち※［＃半濁点付き片仮名カ、1-5-87］...
    input_str = "ち※［＃半濁点付き片仮名カ、1-5-87］※［＃半濁点付き片仮名キ、1-5-88］※［＃半濁点付き片仮名ク、1-5-89］※［＃半濁点付き片仮名ケ、1-5-90］※［＃半濁点付き片仮名コ、1-5-91］"  # noqa: E501
    input_bytes = input_str.encode("shift_jis_2004")

    # Expected: "ちカ゚キ゚ク゚ケ゚コ゚"
    # Using Combining Katakana-Hiragana Semi-Voiced Sound Mark (U+309A)
    # 1-5-87: 3-2577 -> U+30AB U+309A

    expected = "ちカ\u309aキ\u309aク\u309aケ\u309aコ\u309a"

    converted = convert_content(input_bytes)

    # We expect failure initially if the table maps 3-2577 to 'カ' (U+30AB) only.
    assert converted == expected, f"Expected {expected!r}, gave {converted!r}"
