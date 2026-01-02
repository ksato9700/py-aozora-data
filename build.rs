use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::Path;

fn main() {
    let out_dir = env::var("OUT_DIR").unwrap();
    let dest_path = Path::new(&out_dir).join("gaiji_map.rs");
    let mut file = BufWriter::new(File::create(&dest_path).unwrap());

    let table_path = Path::new("jisx0213-2004-std.txt");

    // Safety check: if file doesn't exist, we might want to warn or fail.
    // Assuming it exists because we downloaded it.
    if !table_path.exists() {
        panic!("jisx0213-2004-std.txt not found. Please download it.");
    }

    let input = File::open(table_path).unwrap();
    let reader = BufReader::new(input);

    let mut map = phf_codegen::Map::new();

    // Regex to parse lines: 3-XXXX  U+XXXX
    // But in build.rs we probably want to avoid heavy regex if simple split works?
    // Format: 3-2121	U+3000
    for line in reader.lines() {
        let line = line.unwrap();
        if line.starts_with('#') || line.trim().is_empty() {
            continue;
        }

        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 2 {
            let key = parts[0]; // e.g., "3-2121"
            let val_str = parts[1]; // e.g., "U+3000"

            if val_str.starts_with("U+") {
                let hex_val = &val_str[2..];
                if let Ok(u_val) = u32::from_str_radix(hex_val, 16) {
                    if let Some(c) = std::char::from_u32(u_val) {
                        let c_string = c.to_string();
                        map.entry(key.to_string(), &format!("{:?}", c_string));
                    }
                }
            }
        }
    }

    write!(
        &mut file,
        "static GAIJI_TABLE: phf::Map<&'static str, &'static str> = {};\n",
        map.build()
    ).unwrap();

    println!("cargo:rerun-if-changed=jisx0213-2004-std.txt");
}
