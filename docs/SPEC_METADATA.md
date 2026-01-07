# 1：現代的な <meta> タグ形式
現在の書き方を活かしつつ、最新の推奨（dcterms）に書き換える

```html
<head>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="./aozora.css" />
    <title>十円札 (芥川龍之介)</title>

    <link rel="schema.dcterms" href="http://purl.org/dc/terms/" />

    <meta name="dcterms.title" content="十円札" />
    <meta name="dcterms.creator" content="芥川龍之介" />
    <meta name="dcterms.publisher" content="青空文庫" />
    <meta name="dcterms.type" content="Text" />
    <meta name="dcterms.language" content="jpn" />
    <meta name="dcterms.license" content="https://www.aozora.gr.jp/guide/kijyunn.html" />
</head>
```

ポイント: DC. よりも dcterms. を使うことが現在は推奨されている。

# 2：JSON-LD を追加する
検索エンジン（Googleなど）が内容を正しく理解し、検索結果に著者名などを表示しやすくするため

```html
<head>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="./aozora.css" />
    <title>十円札 (芥川龍之介)</title>

    <script type="application/ld+json">
    {
      "@context": {
        "schema": "https://schema.org/",
        "dcterms": "http://purl.org/dc/terms/"
      },
      "@type": "schema:Book",
      "schema:name": "十円札",
      "schema:author": {
        "@type": "schema:Person",
        "name": "芥川龍之介"
      },
      "schema:publisher": {
        "@type": "schema:Organization",
        "name": "青空文庫"
      },
      "dcterms:language": "jpn",
      "dcterms:format": "text/html"
    }
    </script>
</head>
```