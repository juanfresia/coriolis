#include <utils/GlobalConfig.h>
#include <utils/ConcuMath.h>
#include "DistributionsManager.h"
#include "Flower.h"
#include "DistributionCenter.h"

// @has_checkpoints


DistributionsManager::DistributionsManager() :
        protocol(CHANNEL_DISTRIBUTION_CENTER_MANAGER, NAMED_PIPE_READ),
        logPipe(LOG_WRITE, E_DISTRIBUTION_MANAGER) {

}

DistributionsManager::~DistributionsManager() {
    logPipe << "Destructor" << END_LINE;
    this->waitDistributionsCenterEnd();
}

void DistributionsManager::waitDistributionsCenterEnd(void) {
    // Wait for child process
    for (const pid_t processId: this->processIds) {
        int childResult;
        waitpid(processId, &childResult, 0);
        logPipe << "Distribution center process " << processId << " finished with " << childResult << END_LINE;
    }
}

void DistributionsManager::start() {
    this->spawnCenters();
    bool quit = false;
    bool pause = false;

    std::string msg;

    while (!quit) {
        logPipe << "Waiting for event." << END_LINE;
        event_t event = this->protocol.getEventType();

        if (event == EVENT_USER) {
            action_t action = this->protocol.getAction();

            switch (action) {
                case ACTION_QUIT: {
                    logPipe << "Action Quit Received." << END_LINE;
                    this->sendActionToCenters(action);
                    quit = true;
                    break;
                }

                case ACTION_PAUSE: {
                    if (!pause) {
                        logPipe << "Action Pause Received." << END_LINE;
                        pause = true;
                        this->sendActionToCenters(action);
                        break;
                    }
                }

                case ACTION_RESUME: {
                    if (pause) {
                        logPipe << "Action Resume Received." << END_LINE;
                        pause = false;
                        this->sendActionToCenters(action);
                        break;
                    }
                }

                default: {
                    logPipe << "Don't know action: " << action << END_LINE;
                }
            }
        }

        if (event == EVENT_BOX) {
            std::vector<Flower> flowerBox = this->protocol.receiveFlowersBox();
            if (pause) continue;
            logPipe << "Received box from producer with: " << flowerBox.size() << " number of flowers" << END_LINE;
            distribution_id randomDistribution = ConcuMath::getRandomInt(1, this->distributionsCenterAmount);
            logPipe << "Sending box to random distribution center - Id: " << randomDistribution << END_LINE;
            shared_ptr<Pipe> pipeWrite = this->centerPipesWrite[randomDistribution];
            // @checkpoint prod_send_box flowerBox.front().getProducerId() flowerBox.front().getFlowerId() randomDistribution
            protocol.sendFlowersBox(flowerBox, *pipeWrite);
        }
    }

    return;
}

void DistributionsManager::spawnCenters() {
    unsigned int amount = GlobalConfig::getConfig()->maxDistributionCenters;

    logPipe << "I will create " << amount << " distribution centers." << END_LINE;

    for (size_t i = 0 ; i < amount ; i++) {
        shared_ptr<Pipe> pipe = shared_ptr<Pipe>(new Pipe());
        distribution_id distributionId = i + 1;
        this->centerPipesWrite[distributionId] = pipe;

        pid_t pid = fork();

        if (pid == 0) {
            {
                DistributionCenter center(distributionId, DistributionCenter::randName(), *pipe);
                logPipe << "I created " << center.describe() << END_LINE;
                center.start();
            }
            exit(0);
        } else {
            this->processIds.push_back(pid);
        }
    }

    logPipe << "Finish creating " << amount << " distribution centers" << END_LINE;

    this->distributionsCenterAmount = amount;
}

void DistributionsManager::sendActionToCenters(action_t action) {
    std::map<distribution_id , shared_ptr<Pipe>>::iterator it;
    for (it = this->centerPipesWrite.begin() ; it != this->centerPipesWrite.end() ; ++it) {
        this->protocol.sendActionWithHeaderEvent(action, *it->second);
    }
}


