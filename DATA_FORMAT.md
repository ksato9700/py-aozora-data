# Aozora Bunko Data Format (Firestore)

This document describes the data format used by the `py-aozora-data` importer when storing Aozora Bunko data into Google Cloud Firestore.

## Overview

The data is organized into three main collections in Firestore:
- `books`: Stores information about each book.
- `persons`: Stores information about authors, translators, etc.
- `contributors`: Links books and persons with a specific role (e.g., Author, Translator).

There is also a configuration collection used for tracking import state.

## Collections

### 1. `books` Collection
**Document ID**: `book_id` (Integer as String, e.g., "1234")

| Field | Type | Description |
|---|---|---|
| `book_id` | Integer | Unique identifier for the book |
| `title` | String | Title of the book |
| `title_yomi` | String | Reading (Yomi) of the title |
| `title_sort` | String | Sort key for the title |
| `subtitle` | String | Subtitle |
| `subtitle_yomi` | String | Reading of the subtitle |
| `original_title` | String | Original title (if translated) |
| `first_appearance` | String | First publication info |
| `ndc_code` | String | NDC (Nippon Decimal Classification) code |
| `font_kana_type` | String | Font/Kana usage type (e.g., "新字新仮名") |
| `copyright` | Boolean | `true` if under copyright, `false` otherwise |
| `release_date` | Date/String | Release date on Aozora Bunko |
| `last_modified` | Date/String | Last modified date of the card info |
| `card_url` | String | URL to the Aozora Bunko card page |
| `text_url` | String | URL to the plain text file |
| `html_url` | String | URL to the HTML file |
| `base_book_1` | String | Information about the base book used |
| `input` | String | Name of the person who input the text |
| `proofing` | String | Name of the person who proofread the text |
| ... | ... | *Various other metadata fields from CSV* |

### 2. `persons` Collection
**Document ID**: `person_id` (Integer as String, e.g., "567")

| Field | Type | Description |
|---|---|---|
| `person_id` | Integer | Unique identifier for the person |
| `first_name` | String | First name |
| `last_name` | String | Last name |
| `last_name_yomi` | String | Reading of the last name |
| `first_name_yomi` | String | Reading of the first name |
| `first_name_sort`| String | Sort key for first name |
| `last_name_sort` | String | Sort key for last name |
| `first_name_roman`| String | Romaji first name |
| `last_name_roman` | String | Romaji last name |
| `date_of_birth` | String | Date of birth |
| `date_of_death` | String | Date of death |
| `author_copyright`| Boolean | `true` if author textual copyright exists |

### 3. `contributors` Collection
**Document ID**: `{book_id}-{person_id}-{role_id}` (e.g., "1234-567-0")

| Field | Type | Description |
|---|---|---|
| `id` | String | Composite ID |
| `book_id` | Integer | ID of the book |
| `person_id` | Integer | ID of the person |
| `role` | Integer | Role ID (see Role Mapping below) |

**Role Mapping**:
- `0`: 著者 (Author)
- `1`: 翻訳者 (Translator)
- `2`: 編者 (Editor)
- `3`: 校訂者 (Revisor)
- `4`: その他 (Other)

### 4. `config` Collection
Used for internal state tracking.

**Document ID**: `import_state`
- `last_modified`: (String) The `last_modified` date of the most recently processed entry. Used as a watermark for incremental updates.
