use std::fs::OpenOptions;
use std::io::prelude::*;

const CORIOLIS_LOGGER_OUTPUT_FILE: &str = "/logs/coriolis_run.log";


pub fn coriolis_logger_write(log_line: String) {
    let mut file = OpenOptions::new()
        .append(true)
        .create(true)
        .open(CORIOLIS_LOGGER_OUTPUT_FILE)
        .unwrap();

    if let Err(e) = write!(file, "{}", log_line) {
        eprintln!("CORIOLIS COULDN'T WRITE TO FILE! ERROR: {}", e);
    }	
}
