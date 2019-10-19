//
// Created by demian on 22/9/19.
//

#include <utils/GlobalConfig.h>
#include <utils/ConcuMath.h>
#include "Client.h"

// @has_checkpoints

Client::Client(Pipe &pr) :
    pipeWithManagerRead(pr),
    logPipe(LOG_WRITE, E_CLIENT),
    protocol(CHANNEL_CLIENT_MANAGER, NAMED_PIPE_WRITE) {

    this->createdOrders = 0;
}

void Client::pause(bool * quit) {
    //logPipe << this->name << " (ID: " << this->id << ") is paused" << END_LINE;
    action_t action = this->protocol.getAction(this->pipeWithManagerRead);

    switch (action) {
        case ACTION_RESUME: {
            logPipe << "Client will resume" << END_LINE;
            return;
        }

        case ACTION_QUIT: {
            *quit = true;
            return;
        }

        default:
            this->pause(quit);
    }
}

void Client::start() {
    float sleepTime = GlobalConfig::getConfig()->clientSleepTime;
    bool quit = false;

    while (!quit) {
        int timeToSleep = ConcuMath::getRandomInt(sleepTime, sleepTime * 2);
        logPipe << "Client will try to generate an order the next " << timeToSleep << " seconds" << END_LINE;
        sleep(sleepTime);

        try {
            Order newOrder = this->tryGenerateOrder();

            logPipe << "New order created: " << newOrder.describe() << END_LINE;

            // Send order
            this->protocol.sendBuyOrder(newOrder);

            // Wait for manager response
            logPipe << "Client waiting for action" << END_LINE;
            action_t action = this->protocol.getAction(this->pipeWithManagerRead);
            logPipe << "Client received action: '" << action << "'" << END_LINE;

            switch (action) {
                case ACTION_CONTINUE: {
                    continue;
                }

                case ACTION_PAUSE: {
                    this->pause(&quit);
                    break;
                }

                case ACTION_QUIT: {
                    quit = true;
                    break;
                }

                default: {
                    logPipe << "Client does not know action: '" << action << "'" << END_LINE;
                }
            }

        } catch (std::exception exception) {
            continue;
        }
    }

    logPipe << "Client will quit" << END_LINE;
    exit(0);
}

Order Client::tryGenerateOrder() {
    GlobalConfig* Config = GlobalConfig::getConfig();

    const float clientFailOrderProbability = Config->clientFailOrderProbability;

    const float failNumber = ConcuMath::getRandomFloat(0.0f, 100.0f);

    // Check for fail
    if (failNumber < clientFailOrderProbability) {
        logPipe << "Client skipped the order" << END_LINE;
        throw std::exception();
    }

    // Increment harvested flowers
    this->createdOrders ++;

    return Order::createOrderByType(E_ORDER_LOCAL, this->createdOrders);
}
