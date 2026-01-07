# ruff: noqa: RUF001, RUF003
import pathlib

from aozora_data.text_to_html.converter import TextToHtmlConverter


def test_html5_header_structure(tmp_path: pathlib.Path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.html"

    input_content = "TITLE\nAUTHOR\n\nBODY START"
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    # Check for HTML5 DOCTYPE and structure
    assert "<!DOCTYPE html>" in output_content
    assert '<html lang="ja">' in output_content
    assert '<meta charset="UTF-8" />' in output_content
    assert "<?xml" not in output_content
    assert "xmlns" not in output_content.split("<html")[1].split(">")[0]  # Check html tag attributes


def test_void_elements(tmp_path: pathlib.Path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.html"

    # \n becomes <br>
    # ［＃改ページ］ becomes <hr>
    input_content = "TITLE\nAUTHOR\n\nLine1\nLine2［＃改ページ］Line3"
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    assert "<br>" in output_content
    assert "<br />" not in output_content
    assert "<hr>" in output_content
    assert "<hr />" not in output_content


def test_metadata_extraction(tmp_path: pathlib.Path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.html"

    input_content = "吾輩は猫である\n夏目 漱石\n\n本文"
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    assert "<title>吾輩は猫である (夏目 漱石)</title>" in output_content
    assert '<h1 class="title">吾輩は猫である</h1>' in output_content
    assert '<h2 class="author">夏目 漱石</h2>' in output_content
