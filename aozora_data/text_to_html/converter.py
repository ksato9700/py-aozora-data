# ruff: noqa: RUF001, RUF003
import html
import json
import re
from typing import Any, TextIO


class CharStream:
    """Character stream for parsing Aozora Bunko text."""

    def __init__(self, file_obj: TextIO) -> None:
        """Initialize the character stream."""
        self.file_obj = file_obj
        self.buffer: list[str] = []
        self.eof = False

    def read(self) -> str | None:
        """Read a character from the stream."""
        if self.buffer:
            return self.buffer.pop(0)
        if self.eof:
            return None
        c = self.file_obj.read(1)
        if not c:
            self.eof = True
            return None
        return c

    def peek(self) -> str | None:
        """Peek at the next character in the stream."""
        if self.buffer:
            return self.buffer[0]
        if self.eof:
            return None
        c = self.file_obj.read(1)
        if not c:
            self.eof = True
            return None
        self.buffer.append(c)
        return c

    def read_until(self, terminator: str) -> str:
        """Read characters from the stream until the terminator is found."""
        res = []
        while True:
            c = self.read()
            if c is None:
                break
            if c == terminator:
                break
            res.append(c)
        return "".join(res)


class TextToHtmlConverter:
    """Convert Aozora Bunko text to HTML5."""

    def __init__(self, input_path: str, output_path: str) -> None:
        """Initialize the converter."""
        self.input_path = input_path
        self.output_path = output_path
        self.metadata: dict[str, str] = {}
        self.stream: CharStream | None = None
        self.buffer: list[dict[str, Any]] = []  # List of {'text': str, 'safe': bool}
        self.indent_stack: list[str] = []
        self.ruby_rb_start: int | None = None

    def convert(self) -> None:
        """Convert the input file to XHTML."""
        with (
            open(self.input_path, encoding="utf-8") as f_in,
            open(self.output_path, "w", encoding="utf-8", newline="\r\n") as f_out,
        ):
            self.stream = CharStream(f_in)
            self._parse_header()
            self._write_html_header(f_out)
            self._parse_and_write_body(f_out)
            self._write_footer(f_out)

    def _parse_header(self) -> None:
        if not self.stream:
            return
        lines: list[str] = []
        current: list[str] = []
        while True:
            c = self.stream.read()
            if c is None:
                break
            if c == "\n":
                s = "".join(current).strip()
                if not s:
                    if lines:
                        break
                else:
                    lines.append(s)
                current = []
            else:
                current.append(c)
        self._process_header(lines)

    def _process_header(self, lines: list[str]) -> None:
        info = {}
        if not lines:
            return
        info["title"] = lines[0]
        for line in lines[1:]:
            if "author" not in info and not self._is_orig(line):
                info["author"] = line
            elif line.endswith("訳"):
                info["translator"] = line
            elif any(line.endswith(x) for x in ["編", "編集", "校訂"]):
                info["editor"] = line
            elif self._is_orig(line):
                info["original_title" if "original_title" not in info else "original_subtitle"] = line
            else:
                info["subtitle" if "subtitle" not in info else "original_subtitle"] = line
        self.metadata = info

    def _is_orig(self, t: str) -> bool:
        try:
            t.encode("ascii")
            return True
        except UnicodeEncodeError:
            return False

    def _write_html_header(self, f: TextIO) -> None:
        t = self.metadata.get("title", "")
        a = self.metadata.get("author", "")
        ft = f"{t} ({a})" if a else t
        f.write(f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<link rel="stylesheet" href="./aozora.css" />
<title>{html.escape(ft)}</title>
<link rel="schema.dcterms" href="http://purl.org/dc/terms/" />
<meta name="dcterms.title" content="{html.escape(t)}" />
<meta name="dcterms.creator" content="{html.escape(a)}" />
<meta name="dcterms.publisher" content="青空文庫" />
<meta name="dcterms.type" content="Text" />
<meta name="dcterms.language" content="jpn" />
<meta name="dcterms.license" content="https://www.aozora.gr.jp/guide/kijyunn.html" />
<script type="application/ld+json">
{
            json.dumps(
                {
                    "@context": {
                        "schema": "https://schema.org/",
                        "dcterms": "http://purl.org/dc/terms/",
                    },
                    "@type": "schema:Book",
                    "schema:name": t,
                    "schema:author": {"@type": "schema:Person", "name": a},
                    "schema:publisher": {"@type": "schema:Organization", "name": "青空文庫"},
                    "dcterms:language": "jpn",
                    "dcterms:format": "text/html",
                },
                indent=2,
                ensure_ascii=False,
            )
        }
</script>
</head>
<body>
<div class="metadata">
<h1 class="title">{html.escape(t)}</h1>
""")
        for k in ["original_title", "subtitle", "author", "editor", "translator"]:
            if (v := self.metadata.get(k)) and k != "title":
                f.write(f'<h2 class="{k}">{html.escape(v)}</h2>\n')
        f.write('</div>\n<div class="main_text">')

    def _parse_and_write_body(self, f: TextIO) -> None:
        if not self.stream:
            return
        while True:
            c = self.stream.read()
            if c is None:
                self._flush(f)
                break

            if c == "［":
                self._handle_bracket(f)
            elif c == "《":
                ruby = self.stream.read_until("》")
                self._handle_ruby(ruby)
            elif c == "｜":
                self.ruby_rb_start = len(self.buffer)
            elif c == "※":
                self._handle_note_symbol()
            elif c == "\n":
                self._flush(f)
                f.write("<br>\n")
            else:
                self._append(c)

    def _handle_bracket(self, f: TextIO) -> None:
        if self.stream and self.stream.peek() == "＃":
            self.stream.read()
            cmd = self.stream.read_until("］")
            self._handle_cmd(cmd, f)
        else:
            self._append("［")

    def _handle_note_symbol(self) -> None:
        if self.stream and self.stream.peek() == "［":
            self.stream.read()  # Bracket
            if self.stream.peek() == "＃":
                self.stream.read()  # Sharp
                note = self.stream.read_until("］")
                self._append(f'<span class="notes">［＃{html.escape(note)}］</span>', raw=True)
            else:
                self._append("※［")
        else:
            self._append("※")

    def _append(self, text: str, raw: bool = False) -> None:
        self.buffer.append({"text": text, "safe": raw})

    def _flush(self, f: TextIO) -> None:
        if not self.buffer:
            return
        # Logic to check for "底本："
        full_text = "".join([x["text"] for x in self.buffer])
        if full_text.strip().startswith("底本："):
            f.write('</div>\n<div class="bibliographical_information">\n<hr>\n<br>\n')

        for item in self.buffer:
            f.write(item["text"] if item["safe"] else html.escape(item["text"]))
        self.buffer = []
        self.ruby_rb_start = None

    def _handle_cmd(self, cmd: str, f: TextIO) -> None:
        if cmd.startswith("ここから"):
            self._flush(f)
            cls = "jisage" if "字下げ" in cmd else "keigakomi" if "罫囲み" in cmd else "block"
            # Extract depth for jisage? "ここから１字下げ"
            if m := re.search(r"([０-９]+)字下げ", cmd):
                cls = f"jisage_{self._kanji_num(m.group(1))}"
            f.write(f'<div class="{cls}">')
            self.indent_stack.append(cls)
        elif cmd.endswith("終わり") and cmd != "文頭":
            self._flush(f)
            if self.indent_stack:
                self.indent_stack.pop()
                f.write("</div>")
        elif "見出し" in cmd:
            self._flush(f)
            # Check size
            tag = "h5"
            if "大" in cmd:
                tag = "h3"
            elif "中" in cmd:
                tag = "h4"
            f.write(f'<{tag} class="midashi">{cmd}</{tag}>')
        elif "改ページ" in cmd:
            self._flush(f)
            f.write('<hr>\n<div class="page_break"></div>')
        else:
            pass

    def _handle_ruby(self, ruby: str) -> None:
        if self.ruby_rb_start is not None:
            # Slice buffer
            rb_items = self.buffer[self.ruby_rb_start :]
            del self.buffer[self.ruby_rb_start :]
            rb = "".join([x["text"] for x in rb_items])
            self.ruby_rb_start = None
        else:
            # Backtrack
            rb_list: list[str] = []
            last_type = None

            # Pop from buffer
            while self.buffer:
                item = self.buffer[-1]
                if item["safe"]:
                    break  # Tag stops ruby scope

                t = item["text"]
                ctype = self._get_type(t)
                if last_type is None:
                    last_type = ctype
                elif ctype != last_type:
                    break

                if ctype == "other":  # Punctuation stops ruby
                    break

                rb_list.insert(0, self.buffer.pop()["text"])

            rb = "".join(rb_list)

        self._append(
            f"<ruby><rb>{rb}</rb><rp>（</rp><rt>{html.escape(ruby)}</rt><rp>）</rp></ruby>", raw=True
        )

    def _get_type(self, s: str) -> str:
        # kanji, hiragana, katakana, alpha
        if not s:
            return "other"
        c = s[0]
        if "a" <= c <= "z" or "A" <= c <= "Z":
            return "alpha"
        if "\u3040" <= c <= "\u309f":
            return "hira"
        if "\u30a0" <= c <= "\u30ff":
            return "kata"
        if "\u4e00" <= c <= "\u9fff" or c == "々":
            return "kanji"
        return "other"

    def _kanji_num(self, s: str) -> str:
        tr = str.maketrans("０１２３４５６７８９", "0123456789")
        return s.translate(tr)

    def _write_footer(self, f: TextIO) -> None:
        f.write("</div>\n</body>\n</html>\n")
