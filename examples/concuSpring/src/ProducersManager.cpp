#include <unistd.h>
#include <fcntl.h>
#include <fcntl.h>
#include "ProducersManager.h"
#include "FlowerProducer.h"
#include "protocol/Pipe.h"
#include "Flower.h"
#include "utils/GlobalConfig.h"
#include "protocol/FlowerProtocol.h"

// @has_checkpoints


ProducersManager::ProducersManager() :
    protocol(CHANNEL_PRODUCER_MANAGER, NAMED_PIPE_READ),
    distributionProtocol(CHANNEL_DISTRIBUTION_CENTER_MANAGER, NAMED_PIPE_WRITE),
    logPipe(LOG_WRITE, E_PRODUCER_MANAGER) {

}

ProducersManager::~ProducersManager() {
    logPipe << "Destructor" << END_LINE;
    this->waitProducersEnd();
}

void ProducersManager::waitProducersEnd() {
    // Wait for child process
    for (size_t i = 0 ; i < this->processIds.size() ; i++) {
        int childResult;
        waitpid(this->processIds[i], &childResult, 0);
        logPipe << "Producer process " << this->processIds[i] << " finished with " << childResult << END_LINE;
    }
}

void ProducersManager::start() {
    this->spawnProducers();
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
                    this->sendActionToProducers(action);
                    quit = true;
                    break;
                }

                case ACTION_PAUSE: {
                    if (!pause) {
                        logPipe << "Action Pause Received." << END_LINE;
                        pause = true;
                        this->sendActionToProducers(action);
                        break;
                    }
                }

                case ACTION_RESUME: {
                    if (pause) {
                        logPipe << "Action Resume Received." << END_LINE;
                        pause = false;
                        this->sendActionToProducers(action);
                        break;
                    }
                }

                default: {
                    logPipe << "Don't know action" << END_LINE;
                }
            }
        }

        if (event == EVENT_SIMULATOR) {
            logPipe << "Processing simulator event. Waiting for flower" << END_LINE;
            Flower flower = this->protocol.receiveFlower();

            if (pause) continue;

            logPipe << "Received flower: " << flower.describe() << END_LINE;
            producer_id producerId = flower.getProducerId();

            std::map<producer_id, shared_ptr<Pipe>>::iterator it = this->producersPipesWrite.find(producerId);
            if (it != this->producersPipesWrite.end()) {
                logPipe << "I will notify Continue to producer: " << producerId << END_LINE;
                this->protocol.sendAction(ACTION_CONTINUE, *it->second);
            } else {
                logPipe << "Could not find Pipe for producer: " << producerId << END_LINE;
            }

            this->updateProducer(producerId, flower);
        }
    }

    return;
}

void ProducersManager::sendActionToProducers(action_t action) {
    std::map<producer_id, shared_ptr<Pipe>>::iterator it;
    for (it = this->producersPipesWrite.begin() ; it != this->producersPipesWrite.end() ; ++it) {
        this->protocol.sendAction(action, *it->second);
    }
}

void ProducersManager::spawnProducers() {
    unsigned int amount = GlobalConfig::getConfig()->maxFlowerProducers;

    logPipe << "I will create " << amount << " producers." << END_LINE;


    for (size_t i = 0 ; i < amount ; i++) {
        shared_ptr<Pipe> pipe = shared_ptr<Pipe>(new Pipe());
        producer_id producerId = i + 1;
        this->producersPipesWrite[producerId] = pipe;

        pid_t pid = fork();

        if (pid == 0) {
            {
                FlowerProducer producer(producerId, FlowerProducer::randName(), *pipe);
                logPipe << "I created " << producer.describe() << END_LINE;
                producer.start();
            }
            exit(0);
        } else {
            this->processIds.push_back(pid);
        }
    }
}

void ProducersManager::updateProducer(producer_id producerId, Flower & flower) {
    logPipe << "Updating producer (ID: " << producerId << ")" << END_LINE;

    // Add the flower to the box
    this->producersFlowerBoxes[producerId].push_back(flower);
    // @checkpoint prod_box_bouquet producerId flower.getFlowerId() this->producersFlowerBoxes[producerId].front().getFlowerId() flower.getFlowerName()

    if (this->producersFlowerBoxes[producerId].size() == MAX_BOX_SIZE) {
        distributionProtocol.sendFlowersBox(this->producersFlowerBoxes[producerId]);
        logPipe << "Producer (ID: " << producerId << ")" << " finished and sent a box with " << MAX_BOX_SIZE << " flowers" << END_LINE;
        this->clearProducerBox(this->producersFlowerBoxes[producerId]);
    }

    // Increment counter
    this->producersStats[producerId].flowersProduced++;
    logPipe << "Producer (ID: " << producerId << ") produced " << this->producersStats[producerId].flowersProduced << " flowers" << END_LINE;
    if (flower.getType() == FLOWER_ROSE) this->producersStats[producerId].rosesProduced++;
    if (flower.getType() == FLOWER_TULIP) this->producersStats[producerId].tulipProduced++;
}

void ProducersManager::clearProducerBox(std::vector<Flower> & box) {
    box.clear();
}
