// @has_checkpoints

use std::{thread, time};
use std::thread::JoinHandle;
use std::sync::{Mutex, Arc, mpsc};
use std::collections::HashMap;

use network::message::{Message};

const SECONDS: usize = 0;
const QUADRANT_QTY: usize = 1;
const QUADRANTS_PER_SERVER: usize = 2;
const INVALID_ID_PHOTO: isize = -1;


pub struct Observatory {
	id: isize,
    total_time: f64,
    events: f64,
	avg_time: Arc<Mutex<f64>>,
	quadrant_qty: usize,
	seconds: usize,
	quadrants_per_server: Vec<i32>,
	rx: mpsc::Receiver<Message>,
	tx: mpsc::Sender<Message>,
	servers_senders: Vec<mpsc::Sender<Message>>
}

impl Observatory {
	pub fn new(id:usize, init_time: Arc<Mutex<f64>>) -> Observatory {
		let (tx, rx): (mpsc::Sender<Message>, mpsc::Receiver<Message>) = mpsc::channel();
		Observatory { id:id as isize,
			rx:rx, tx:tx, servers_senders:Vec::new(),
			total_time:0.0, 
			events:0.0, 
			avg_time: init_time, 
			quadrant_qty:0, 
			seconds:0,
			quadrants_per_server:Vec::new()
		}
	}

	pub fn set_servers_senders(&mut self, servers_senders: Vec<mpsc::Sender<Message>>){
		self.servers_senders = servers_senders;
	}

	pub fn get_sender(&self) -> mpsc::Sender<Message>{
		return mpsc::Sender::clone(&self.tx);
	}

	fn run_sender(&self, running: & Arc<Mutex<bool>>) -> JoinHandle<i32> {
		let running_s = Arc::clone(running);

		let _id = self.id; 
		let _quadrants_per_server = self.quadrants_per_server.clone();
		let _servers_senders = self.servers_senders.clone();
		let _seconds = self.seconds;

		let sender = thread::spawn(move || {
			let mut id_message = 0;
			while {*running_s.lock().unwrap()} {
				let mut server_number = 0;
				let now = time::Instant::now();
				let _message = Message{id_observatory: _id, id_photo: id_message, start_time: now };

				for quadrants in &_quadrants_per_server {
					for _i in 0..*quadrants {
						let message = _message.clone();
                		_servers_senders[server_number as usize].send(message).unwrap();
                		// @checkpoint send_to_server _id server_number id_message
                	}
					//thread::sleep(time::Duration::from_millis(500 * (_seconds as u64)));
					server_number += 1;

                }
				thread::sleep(time::Duration::from_millis(500 * (_seconds as u64)));
				id_message += 1;
			}
			for server_tx in _servers_senders {
				let invalid_message = Message{id_observatory: _id, id_photo: -1, start_time: time::Instant::now()};
            	server_tx.send(invalid_message).unwrap();
        	}
			return 0;
    	});
		return sender;
	}

	pub fn run(&mut self, running: &Arc<Mutex<bool>>) {
		let sender = self.run_sender(running);

		let mut sending_messages: HashMap<usize, usize>  = HashMap::new();
		let mut servers_count = self.servers_senders.len();

		loop {
            let valor_recibido = self.rx.recv().unwrap();
			if valor_recibido.id_photo == INVALID_ID_PHOTO { 
				servers_count -= 1;
				if servers_count == 0 { break; }
				continue;
			} else {
		        //println!("Observatory {} received reply for photo {}", self.id, valor_recibido.id_photo);
                // @checkpoint rcv_from_server self.id valor_recibido.id_photo
			}
			self.process_new_messege(&valor_recibido, &mut sending_messages);
        }
		sender.join().unwrap();
		println!("Goodbye from observatory {}", self.id);
	}

	fn process_new_messege(&mut self,message: &Message ,messages: &mut HashMap<usize, usize> ){
		let _id_photo = message.id_photo as usize;
		let mut quadrants_count = *messages.entry(_id_photo).or_insert(0);
		quadrants_count += 1;
		
		if quadrants_count == self.quadrant_qty {
			self.total_time += message.start_time.elapsed().as_secs() as f64;
			self.events += 1.0;
			self.update_avg_time();
			// @checkpoint rcv_full_photo self.id _id_photo self.quadrant_qty
			return;
		}	
		messages.insert(_id_photo, quadrants_count);
	}

	fn update_avg_time(&mut self) {
        let mut time = self.avg_time.lock().unwrap();
        *time = self.total_time / self.events;
	}

	pub fn parse_line(&mut self, line: &str){
		let params: Vec<&str> = line.split(" ").collect();
		self.seconds = params[SECONDS].parse().unwrap();
		self.quadrant_qty = params[QUADRANT_QTY].parse().unwrap();
		// @checkpoint observatory_create self.id self.seconds self.quadrant_qty
		for i in QUADRANTS_PER_SERVER..params.len(){
			self.quadrants_per_server.push(params[i].parse().unwrap());
		};
	}
}


