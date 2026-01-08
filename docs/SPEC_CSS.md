# **青空文庫 CSS Modernization 2026 設計ドキュメント (HTML5版)**

## **1. 概要**

本プロジェクトは、青空文庫（Aozora Bunko）のコンテンツを、HTML5ベースのセマンティックな構造として定義し、2026年現在のブラウザ標準機能を用いて最適に表示するためのスタイルシートを再構築するものである。
従来のXHTML準拠の構造をHTML5のモダンなセマンティクスへマッピングし、アクセシビリティと保守性を極限まで高めたネイティブ・ファーストな設計を採用する。

## **2. 設計原則**

1. **Semantic & Accessible**: `<div>` や `<span>` の多用を避け、`<article>`, `<section>`, `<aside>`, `<figure>`, `<figcaption>` などのHTML5要素を活用して文書構造を明示する。
2. **Native-First Logic**: JavaScriptやプリプロセッサに頼らず、CSS標準機能（Container Queries, `:has()`, `@layer`）で表示ロジックを完結させる。
3. **Typography-Centric**: 最新のCSSプロパティを用い、Webフォントや高度な字詰め、ルビ制御によって「活字の美しさ」をデジタルで再現する。
4. **Logical Layout**: 縦書きと横書きの切り替えを、論理プロパティ（Logical Properties）によって単一のコードベースで実現する。

## **3. システムアーキテクチャ**

### **3.1 カスケードレイヤー (@layer)**

詳細度の競合を排除し、スタイルの役割を明確化する。
```css
@layer reset, tokens, base, semantics, typography, annotations, themes;
```

* **semantics**: HTML5要素（article, section等）に対するデフォルト定義。
* **annotations**: `<ruby>`, `<mark>` および注記クラスの定義。

### **3.2 HTML5要素へのマッピング**

青空文庫特有の構造を以下のHTML5要素として定義・スタイリングする。

* **作品全体**: `<article class="aozora-work">`
* **章・節**: `<section>`
* **見出し**: `<h1>`〜`<h6>`
* **注釈・サイドノート**: `<aside>` または `<details>`
* **図版・挿絵**: `<figure>` と `<figcaption>`
* **ルビ**: `<ruby>`, `<rt>`, `<rp>`

## **4. 主要機能の設計**

### **4.1 コンテナクエリによるコンポーネント最適化**

画面サイズではなく、`<article>` 要素のサイズに応じてレイアウトを動的に変更する。

```css
.aozora-work {
  container-type: inline-size;
  max-inline-size: 60ch; /\* 読みやすい一行の長さを維持 \*/
  margin-inline: auto;
}

/\* 広い画面では自動的に多段組みへ \*/
@container (inline-size \> 1000px) {
  .main-text {
    column-count: 2;
    column-gap: 3rem;
    column-rule: 1px solid var(--border-color);
  }
}
```

### **4.2 セマンティックな `:has()` 制御**

要素の階層構造に基づいた自動スタイリング。

```css
/\* 図版（figure）が連続する場合のレイアウト \*/
section:has(figure \+ figure) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/\* 注釈（aside）が開かれている時の本文のコントラスト調整 \*/
article:has(aside\[open\]) .main-text {
  opacity: 0.7;
  filter: blur(1px);
}
```

### **4.3 高度な和文組版 (HTML5 Native)**

* **Native Ruby**: ruby-position: over や ruby-align: space-around を活用。
* **Text Box Trim**: text-box-trim: both により、見出しや段落の上下余白を厳密に制御。
* **Hanging Punctuation**: hanging-punctuation: allow-end による句読点のぶら下がり制御。

### **4.4 カラー管理 (OKLCH & Light-Dark)**

```css
:root {
  /\* 視認性の高い配色をOKLCHで定義 \*/
  \--bg-color: light-dark(oklch(99% 0.01 80), oklch(12% 0.02 260));
  \--text-color: light-dark(oklch(20% 0.01 80), oklch(92% 0.01 260));
}
```

## **5. 実装ガイドライン**

1. **No More br for Spacing**: 段落間や見出し前後の余白は、CSSの margin-block で制御し、HTML上の空改行は排除する。
2. **SVG for Gaiji**: 外字（JIS外文字）は画像ではなく、インラインSVGまたはカスタムフォントとして扱い、CSSでテキストと整列させる。
3. **Scroll-driven Interaction**: 読書進捗をブラウザ標準のスクロールタイムライン機能で視覚化する。

## **6. 結論**

HTML5への移行により、青空文庫のコンテンツは単なる「表示データ」から、構造化された「デジタルドキュメント」へと進化する。本設計は、最新のCSS機能をセマンティックなHTMLに適用することで、アクセシビリティ、パフォーマンス、そして美的な読書体験を長期にわたって保証するものである。
