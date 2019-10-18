//
// Created by demian on 22/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_CLIENT_H
#define TP1_FIUBA_CONCURRENTE_CLIENT_H


#include "LogPipe.h"
#include "Order.h"
#include "protocol/FlowerProtocol.h"

class Client {
protected:
    class Pipe & pipeWithManagerRead;
    LogPipe logPipe;
    FlowerProtocol protocol;
    order_id createdOrders;

    void pause(bool *);
    Order tryGenerateOrder();
public:
    Client(Pipe &);
    void start();
};


#endif //TP1_FIUBA_CONCURRENTE_CLIENT_H
