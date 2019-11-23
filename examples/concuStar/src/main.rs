use std::io;
use std::thread;
use std::usize;
use std::sync::{Mutex, Arc, mpsc};
use std::io::{BufReader,BufRead};
use std::fs::File;


mod network;
use network::observatory::{Observatory};
use network::server::{Server};
use network::message::{Message};

fn main() {
    println!("------------------------------------------------------------------------------");
    println!("--------------------------------- CONCU-STAR ---------------------------------");
    println!("------------------------------------------------------------------------------");
    println!("Simulation begins...");
    println!("Write the number of observatory to get the average time per image or 'q' to exit");

    let mut avg_times = Vec::new();
    let running = Arc::new(Mutex::new(true));
    let file = File::open("../config.txt").expect("Configuration file not found!");
    let mut reader = BufReader::new(file);
    let mut first_line = String::new();
    let mut observatory_count = 0;    

    let mut children = vec![];
    let mut servers: Vec<Server> = Vec::new();
    let mut senders_observatorios: Vec<mpsc::Sender<Message>> = Vec::new();
    let mut senders_servers: Vec<mpsc::Sender<Message>> = Vec::new();

    reader.read_line(&mut first_line).expect("Unable to read line");
    let servers_time: Vec<&str> = first_line.split_whitespace().collect();
    
    for _s in 0..servers_time.len() {
        let server = Server::new(_s, servers_time[_s].parse().unwrap());
        senders_servers.push(server.get_sender());
        servers.push(server);
    }        

    for line in reader.lines() {
        avg_times.push(Arc::new(Mutex::new(0.0)));
        let avg_time = Arc::clone(&avg_times[observatory_count]);

        let mut obs = Observatory::new(observatory_count, avg_time);
        obs.parse_line(&line.unwrap());
        senders_observatorios.push(obs.get_sender());
        obs.set_servers_senders(senders_servers.clone());

        let _running = Arc::clone(&running);
        children.push(thread::spawn(move || { 
            obs.run(&_running);
            return 0;
        }));

        observatory_count += 1;
    }

    for mut server in servers {
        server.set_observatories_senders(senders_observatorios.clone());

        children.push(thread::spawn(move || { 
            server.run();
            return 0;
        }));
    } 

    loop {
        let mut line = String::new();
        io::stdin().read_line(&mut line).expect("Failed to read line!");
        let user_input: String = line.trim().parse().expect("Wanted a valid string!");

        //Read from stdin until user enters 'q' to exit
        if user_input.to_lowercase() == "q" {
            println!("Received q! Now executing graceful quit...");
            {
                let mut running_val = running.lock().unwrap();
                *running_val = false;
            }

            for handle in children {
                handle.join().unwrap();
            }
            println!("The End!");
            return;
        }

        let input = user_input.parse::<usize>();
        match input {
            Ok(number) => { 
                if number < observatory_count {
                    println!("Average time per image for observatory {} is: {}sec.", number, *avg_times[number].lock().unwrap());
                }else{
                    println!("Please enter a valid observatory number! [0 : {}] or 'q' to exit!", observatory_count-1);
                }
            },
            Err(e) => println!("Wanted a positive number! ({})", e), 
        }
    }
}
