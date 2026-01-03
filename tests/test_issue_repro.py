from aozora_data.sjis_to_utf8 import convert_content

# ruff: noqa: RUF001, RUF003


def test_repro_issue_000104():
    # Read the actual file
    file_path = "/Users/ksato/git/py-aozora-data/sjis/000104.sjis.txt"
    with open(file_path, "rb") as f:
        input_bytes = f.read()

    # Run conversion
    converted = convert_content(input_bytes)

    # The erroneous pattern reported: "譃《うそ》譃」は底本では「謔」］"
    error_pattern = "譃《うそ》譃」は底本では「謔」］"

    if error_pattern in converted:
        # Assert False to signal failure (reproduction)
        raise AssertionError(f"Bug reproduced! Found erroneous pattern: {error_pattern}")

    # Verify the specific part is preserved correctly
    target_part = "［＃「譃」は底本では「謔」］"
    assert target_part in converted, f"Expected '{target_part}' in output, but got incorrect result."
