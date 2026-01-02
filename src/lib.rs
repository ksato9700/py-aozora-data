use pyo3::prelude::*;
use encoding_rs::SHIFT_JIS;
use regex::Regex;
use std::borrow::Cow;
use lazy_static::lazy_static;

include!(concat!(env!("OUT_DIR"), "/gaiji_map.rs"));

lazy_static! {
    static ref GAIJI_PATTERN_1: Regex = Regex::new(r"第(\d)水準\d-(\d{1,2})-(\d{1,2})").unwrap();
    static ref GAIJI_PATTERN_2: Regex = Regex::new(r"U\+([0-9A-Fa-f]{4})").unwrap();
    static ref ANNOTATION_PATTERN: Regex = Regex::new(r"※［＃.+?］").unwrap();
}

fn get_gaiji(s: &str) -> String {
    // Pattern 1: JIS X 0213 plane/row/cell
    // Example: 第3水準1-84-22
    if let Some(caps) = GAIJI_PATTERN_1.captures(s) {
        let plane: u32 = caps[1].parse().unwrap_or(3); // Default to 3? logic says m[1]
        let row: u32 = caps[2].parse().unwrap_or(0);
        let cell: u32 = caps[3].parse().unwrap_or(0);

        let key = format!("{}-{:2X}{:2X}", plane, row + 32, cell + 32);

        if let Some(&val) = GAIJI_TABLE.get(key.as_str()) {
            return val.to_string();
        }
    }

    // Pattern 2: Direct Unicode Reference
    // Example: U+8EC3
    if let Some(caps) = GAIJI_PATTERN_2.captures(s) {
        if let Ok(u_val) = u32::from_str_radix(&caps[1], 16) {
            if let Some(c) = std::char::from_u32(u_val) {
                return c.to_string();
            }
        }
    }

    // Return original string if no match
    s.to_string()
}

#[pyfunction]
fn convert_content(content: &[u8]) -> PyResult<String> {
    // 1. Decode Shift JIS
    let (cow, _encoding_used, _had_errors) = SHIFT_JIS.decode(content);
    let decoded = cow.as_ref();

    // 2. Replace Gaiji annotations
    // Regex replace_all with a callback-like logic?
    // regex crate's replace_all takes a Replacer trait. Pattern is "※［＃.+?］"

    let result = ANNOTATION_PATTERN.replace_all(decoded, |caps: &regex::Captures| {
        let match_str = &caps[0];
        get_gaiji(match_str)
    });

    Ok(result.into_owned())
}

#[pymodule]
fn _sjis_to_utf8(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(convert_content, m)?)?;
    Ok(())
}
