#[derive(Debug, Clone)]
pub struct Message {
	pub id_observatory: isize,
    pub id_photo: isize,
	pub start_time: std::time::Instant
}
