// @has_checkpoints

use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::sync::{Mutex, Arc};

const MAX_EATING_TIME: u32 = 411;
const MAX_THINKING_TIME: u32 = 411;

const PHILOS_AMOUNT: usize = 7;
const PHILOS_ROUNDS: usize = 4;

const PHILOS_NAMES: [&'static str; 10] = [
	"Karl", "Immanuel", "Rene", "John", "Thomas", "Jean", "Friedrich", "Richard", "Gottfried", "Francis"
	];
const PHILOS_SURNAMES: [&'static str; 10] = [
	"Marx", "Kant", "Descartes", "Locke", "Hobbes", "Rousseau", "Nietzsche", "Bentle", "Leibniz", "Bacon"
	];

fn rand_int(n: u32) -> u32 {
    let nanos: u32 = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .subsec_nanos();
    (nanos / 1111) % n
}

fn sleep_rand_int(max_time: u32) {
    let t = rand_int(max_time);
    thread::sleep(Duration::from_millis(t as u64));
}


struct Philosopher {
    name: String,
    surname: String,
    left: usize,
    right: usize,
}

impl Philosopher {
    fn new(name: &str, surname: &str, left: usize, right: usize) -> Philosopher {
        Philosopher {
            name: name.to_string(),
            surname: surname.to_string(),
            left: left,
            right: right,
        }
    }

    fn main(&self, table: &Table, round: usize) {
		let fullname = format!("{}{}", self.name, self.surname);
        println!("{} is thinking", fullname);
        // @checkpoint think fullname round
        sleep_rand_int(MAX_THINKING_TIME);
        
        let lf = table.forks[self.left].lock().unwrap();
        println!("{} acquired left fork", fullname);
        // @checkpoint acquire_fork fullname self.left round
        let rf = table.forks[self.right].lock().unwrap();
        println!("{} acquired right fork", fullname);
        // @checkpoint acquire_fork fullname self.right round

        println!("{} is eating.", fullname);
        // @checkpoint eat fullname round
        sleep_rand_int(MAX_EATING_TIME);
        

        println!("{} released left fork", fullname);
        // @checkpoint release_fork fullname self.left round
        drop(lf);
        println!("{} released right fork", fullname);
        // @checkpoint release_fork fullname self.right round
        drop(rf);
    }
}

struct Table {
    forks: Vec<Mutex<()>>,
}

fn main() {
    let mut philosophers = Vec::new();
    let mut forks = Vec::new();
    
    for i in 0..PHILOS_AMOUNT {
		let name = PHILOS_NAMES[rand_int(PHILOS_AMOUNT as u32) as usize];
		sleep_rand_int(13);
		let surname = PHILOS_SURNAMES[rand_int(PHILOS_AMOUNT as u32) as usize];
		
		philosophers.push(Philosopher::new(name, surname, i, (i+1)%PHILOS_AMOUNT));
		forks.push(Mutex::new(()));
	}
	
    let table = Arc::new(Table {forks: forks});


    let handles: Vec<_> = philosophers.into_iter().map(|p| {
        let table = table.clone();

        thread::spawn(move || {
			for i in 0..PHILOS_ROUNDS {
				p.main(&table, i);
			}
        })
    }).collect();

    for h in handles {
        h.join().unwrap();
    }
}
