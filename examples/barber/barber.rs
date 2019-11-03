// @has_checkpoints

use std::sync::{Arc, Mutex};
use std::sync::mpsc::{sync_channel};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const SEATS_AMOUNT: usize = 5;
const CUSTOMERS_AMOUNT: usize = 20;
const EXIT_CODE: usize = CUSTOMERS_AMOUNT + 8;
const MAX_HAIRCUT_TIME: u32 = 189;
const MAX_SPAWNING_TIME: u32 = 77;
const MAX_IDLE_TIME: u32 = 57;


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

fn main() {
    let (queue_back, queue_front) = sync_channel::<usize>(0);
    let free_seats  = Arc::new(Mutex::new(SEATS_AMOUNT));
    let free_seats_barber = free_seats.clone();

    // Barber:
    let barber_handle = thread::spawn(move|| {
        for i in queue_front.iter() {
            *free_seats_barber.lock().unwrap() += 1;
            if i == EXIT_CODE {
                println!("The barber closes the shop!");
                return;
            }

            println!("Barber begins cutting customer {}", i);
            // @checkpoint cut_hair i
            sleep_rand_int(MAX_HAIRCUT_TIME);
            println!("Barber finishes cutting customer {}", i);
        }
    });

    // Customers:
    let spawner_handle = thread::spawn(move|| {
        let exit_queue = queue_back.clone();
        let mut customer_handles = vec![];
        for i in 0..CUSTOMERS_AMOUNT {
            sleep_rand_int(MAX_SPAWNING_TIME);

            let free_seats = free_seats.clone();
            let queue_back = queue_back.clone();
            let customer_id = i + 1;

            let customer_handle = thread::spawn(move|| {
                sleep_rand_int(MAX_IDLE_TIME);
                {
                    println!("Customer {} arrived to the shop", customer_id);
                    let mut free_seats = free_seats.lock().unwrap();

                    if *free_seats == 0 {
                        println!("Customer {} gives up and leaves", customer_id);
                        // @checkpoint leave_shop customer_id
                        return;
                    } else {
                        println!("Customer {} sits down and waits", customer_id);
                        // @checkpoint take_seat customer_id
                        *free_seats -= 1;
                    }
                }

                queue_back.send(customer_id).unwrap();
                println!("Customer {} begins getting cut", customer_id);
                // @checkpoint get_hair_cut customer_id
            });

            customer_handles.push(customer_handle);
        }

        for h in customer_handles {
            h.join().unwrap();
        }
        exit_queue.send(EXIT_CODE).unwrap();
    });

    spawner_handle.join().unwrap();
    barber_handle.join().unwrap();
}

