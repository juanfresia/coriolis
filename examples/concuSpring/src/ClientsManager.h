//
// Created by demian on 22/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_CLIENTSMANAGER_H
#define TP1_FIUBA_CONCURRENTE_CLIENTSMANAGER_H

#include "LogPipe.h"
#include "Order.h"
#include "protocol/Pipe.h"
#include "Concurrentes.h"

class ClientsManager {
private:
    FlowerProtocol protocol;
    FlowerProtocol pointOfSaleProtocol;
    LogPipe logPipe;


    shared_ptr<Pipe> clientPipeWrite;
    pid_t clientPid;

    void spawnClients();
public:
    ClientsManager();

    void start();
};


#endif //TP1_FIUBA_CONCURRENTE_CLIENTSMANAGER_H
