use std::thread;
use std::sync::mpsc;
use std::time::Duration;
//use rand::Rng;

mod network;
use network::server::{Server};

#[derive(Debug, Clone)]
pub struct Observatory {
    servers_senders: Vec<mpsc::Sender<i32>>,
    servers_designed: Vec<i32>,
}

fn main2() {
    let cant_observatorios = 3;
    let cant_servidores = 3;

    let mut children = vec![];
    
    let mut observatorios: Vec<Observatory> = Vec::new();
    // let mut servers: Vec<Server> = Vec::new();


    for _o in 0..cant_observatorios {
        observatorios.push(Observatory{servers_senders: Vec::new(), servers_designed: vec![0, 2] });
    }

    // creacion de vectores de canales tx y rx    
    let mut senders_observatorios: Vec<mpsc::Sender<i32>> = Vec::new();
    let mut senders_servers: Vec<mpsc::Sender<i32>> = Vec::new();
    let mut recv_observatorios: Vec<mpsc::Receiver<i32>> = Vec::new();
    //let mut recv_servers: Vec<mpsc::Receiver<i32>> = Vec::new();

    for _o in 0..cant_observatorios {
        let (tx, rx): (mpsc::Sender<i32>, mpsc::Receiver<i32>) = mpsc::channel();
        senders_observatorios.push(tx);
        recv_observatorios.push(rx);
    }
    
    for _s in 0..cant_servidores {
        let mut server = Server::new(_s,2);
        server.set_observatories_senders(senders_observatorios.clone());
        senders_servers.push(server.get_sender());
        
        children.push(thread::spawn(move || { 
            server.run();
        }));
    }
    
    //OBSERVATORIOS
    for _o in 0..cant_observatorios {
        observatorios[_o].servers_senders = senders_servers.clone();
        let _observatorio = observatorios[_o].clone();
        let rx = recv_observatorios.remove(0); 

        children.push(thread::spawn(move || { 
            let observatorio = _observatorio;

            thread::spawn(move || {
                loop {
                    let valor_recibido = rx.recv().unwrap();
                    println!("observatorio {} recibe del server {}", _o, valor_recibido);
                }               
            });
            
            for server in &observatorio.servers_designed {
                println!("observatorio {} envia su numero a server {}", _o, *server);
                observatorio.servers_senders[*server as usize].send(_o as i32).unwrap();
            }
            
        }));
    }

    for child in children {
        // Wait for the thread to finish. Returns a result.
        let _ = child.join().unwrap();
    }
}
