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
    assert '<html lang="ja-JP">' in output_content
    assert '<meta charset="UTF-8" />' in output_content
    assert (
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />' in output_content
    )
    assert "<main>" in output_content
    assert "<article>" in output_content
    assert "</article>" in output_content
    assert "</main>" in output_content
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


def test_metadata_format(tmp_path: pathlib.Path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.html"

    input_content = "十円札\n芥川龍之介\n\n本文"
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    # Check for dcterms meta tags
    assert '<link rel="schema.dcterms" href="http://purl.org/dc/terms/" />' in output_content
    assert '<meta name="dcterms.title" content="十円札" />' in output_content
    assert '<meta name="dcterms.creator" content="芥川龍之介" />' in output_content
    assert '<meta name="dcterms.publisher" content="青空文庫" />' in output_content
    assert '<meta name="dcterms.type" content="Text" />' in output_content
    assert '<meta name="dcterms.language" content="jpn" />' in output_content
    assert (
        '<meta name="dcterms.license" content="https://www.aozora.gr.jp/guide/kijyunn.html" />'
        in output_content
    )

    # Check for absence of old DC tags
    assert 'rel="Schema.DC"' not in output_content
    assert 'name="DC.Title"' not in output_content

    # Check for JSON-LD
    assert '<script type="application/ld+json">' in output_content

    # Basic JSON-LD structure check
    assert '"@type": "schema:Book"' in output_content
    assert '"schema:name": "十円札"' in output_content
    assert '"dcterms:format": "text/html"' in output_content


def test_dash_block_removal(tmp_path: pathlib.Path):
    input_file = tmp_path / "input_with_dash.txt"
    output_file = tmp_path / "output_with_dash.html"

    input_content = """タイトル
著者

-------------------------------------------------------
【テキスト中に現れる記号について】

《》：ルビ
（）：注記
-------------------------------------------------------

本文です。"""
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    assert "本文です。" in output_content
    assert "【テキスト中に現れる記号について】" not in output_content
    assert "-------------------------------------------------------" not in output_content


def test_no_dash_block(tmp_path: pathlib.Path):
    input_file = tmp_path / "input_no_dash.txt"
    output_file = tmp_path / "output_no_dash.html"

    input_content = """タイトル
著者

本文です。"""
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    assert "本文です。" in output_content
    assert "-------------------------------------------------------" not in output_content


def test_semantic_footer(tmp_path: pathlib.Path):
    input_file = tmp_path / "input_footer.txt"
    output_file = tmp_path / "output_footer.html"

    input_content = """タイトル
著者

本文

底本：
青空文庫"""
    input_file.write_text(input_content, encoding="utf-8")

    converter = TextToHtmlConverter(str(input_file), str(output_file))
    converter.convert()

    output_content = output_file.read_text(encoding="utf-8")

    assert "</article>" in output_content
    assert "<footer>" in output_content
    assert '<div class="bibliographical_information">' in output_content
    assert "</footer>" in output_content
    assert output_content.index("</article>") < output_content.index("<footer>")
