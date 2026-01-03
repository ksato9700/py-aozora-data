from aozora_data.sjis_to_utf8 import convert_content

# ruff: noqa: RUF001, RUF003, E501


def test_repro_issue_000061():
    # Read the actual file
    file_path = "/Users/ksato/git/py-aozora-data/sjis/000061.sjis.txt"
    with open(file_path, "rb") as f:
        input_bytes = f.read()

    # Run conversion
    converted = convert_content(input_bytes)

    # User reported:
    # Expected:
    # 大殿樣は...眴《めくば》せを［＃「眴《めくば》せを」は底本では「眗《めくば》せを」］なさいました。
    # Actual:
    # ...眴《めくば》せを眴《めくば》せを」は底本では「眗《めくば》せを」］...

    # Verify the specific part is preserved correctly
    # We look for "［＃「" preceding the string.

    # The string inside the note is "眴《めくば》せを"
    target_snippet = "［＃「眴《めくば》せを」は底本では"

    # If key char is dropped it becomes "眴《めくば》せを」は底本では"

    assert target_snippet in converted, (
        f"Expected '{target_snippet}' in output, but got incorrect result."
    )
