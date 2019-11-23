// @has_checkpoints

use std::thread;
use std::sync:: mpsc;
use std::time::Duration;

use network::message::{Message};

const INVALID_ID_PHOTO: isize = -1;

#[derive(Debug)]
pub struct Server {
	id: usize,
    rx: mpsc::Receiver<Message>,
	tx: mpsc::Sender<Message>,
    pub process_time: usize,
    observatories_senders: Vec<mpsc::Sender<Message>>,
}

impl Server {
	pub fn new(id: usize, process_time: usize) -> Server{ 
		let (tx, rx): (mpsc::Sender<Message>, mpsc::Receiver<Message>) = mpsc::channel();
        //println!("New server {} with time: {}", id, process_time);
        // @checkpoint server_create id process_time
		Server{id:id, rx:rx, tx:tx, process_time:process_time, observatories_senders: Vec::new()}
	}

	pub fn set_observatories_senders(&mut self, observatories_senders: Vec<mpsc::Sender<Message>>){
		self.observatories_senders = observatories_senders;
	}

	pub fn get_sender(&self) -> mpsc::Sender<Message>{
		return mpsc::Sender::clone(&self.tx);
	}

	pub fn run(&mut self) {
		let mut observatories_count = self.observatories_senders.len();

		loop {
        	let valor_recibido = self.rx.recv().unwrap();
            
            thread::sleep(Duration::from_millis(500 * (self.process_time as u64)));
            self.observatories_senders[valor_recibido.id_observatory as usize].send(valor_recibido.clone()).unwrap();
			
			if valor_recibido.id_photo == INVALID_ID_PHOTO { 
				observatories_count -= 1;
				if observatories_count == 0 { break; }
			} else {
			    //println!("Server {} replied to {}", self.id, valor_recibido.id_observatory);
			    // @checkpoint send_to_obs self.id valor_recibido.id_observatory valor_recibido.id_photo
			}

     	}
		println!("Goodbye from server {}", self.id);
	}
}
