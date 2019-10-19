//
// Created by demian on 22/9/19.
//

#include <utils/ConcuMath.h>
#include "ClientsManager.h"
#include "utils/GlobalConfig.h"
#include "Client.h"

ClientsManager::ClientsManager() :
        protocol(CHANNEL_CLIENT_MANAGER, NAMED_PIPE_READ),
        pointOfSaleProtocol(CHANNEL_POINT_OF_SALE_MANAGER, NAMED_PIPE_WRITE),
        logPipe(LOG_WRITE, E_CLIENT_MANAGER) {

}

void ClientsManager::spawnClients() {

    logPipe << "I will create one client." << END_LINE;

    this->clientPipeWrite = shared_ptr<Pipe>(new Pipe());

    pid_t pid = fork();

    if (pid == 0) {
        {
            Client client(*this->clientPipeWrite);
            logPipe << "I created a client" << END_LINE;
            client.start();
        }
        exit(0);
    } else {
        this->clientPid = pid;
    }

}

void ClientsManager::start() {
    this->spawnClients();
    bool quit = false;
    bool pause = false;

    std::string msg;

    while (!quit) {
        logPipe << "Waiting for event." << END_LINE;
        event_t event = this->protocol.getEventType();

        if (event == EVENT_USER) {
            logPipe << "Received user event: " << event << END_LINE;
            action_t action = this->protocol.getAction();

            switch (action) {
                case ACTION_QUIT: {
                    logPipe << "Action Quit Received." << END_LINE;
                    this->protocol.sendAction(action, *this->clientPipeWrite);
                    quit = true;
                    break;
                }

                case ACTION_PAUSE: {
                    if (!pause) {
                        logPipe << "Action Pause Received." << END_LINE;
                        pause = true;
                        this->protocol.sendAction(action, *this->clientPipeWrite);
                        break;
                    }
                }

                case ACTION_RESUME: {
                    if (pause) {
                        logPipe << "Action Resume Received." << END_LINE;
                        pause = false;
                        this->protocol.sendAction(action, *this->clientPipeWrite);
                        break;
                    }
                }

                default: {
                    logPipe << "Don't know action" << END_LINE;
                }
            }
        }

        if (event == EVENT_BUY_ORDER) {
            logPipe << "Processing simulator event. New buy order" << END_LINE;
            Order order = this->protocol.receiveOrder();
            logPipe << "Received order: " << order.describe() << END_LINE;

            if (pause) continue;

            // Send action to client
            this->protocol.sendAction(ACTION_CONTINUE, *this->clientPipeWrite);

            // SEnd the order to the point of sale manager
            this->pointOfSaleProtocol.sendBuyOrder(order);
        }
    }

    return;
}



