#include <protocol/FlowerProtocol.h>
#include "FlowerSimulator.h"
#include "utils/GlobalConfig.h"
#include "ProducersManager.h"
#include "LogPipe.h"
#include "Logger.h"
#include "DistributionsManager.h"
#include "PointOfSalesManager.h"
#include "ClientsManager.h"

FlowerSimulator::FlowerSimulator(const std::string & cp, const std::string & ll) {
    this->pause = false;
    this->quit = false;
    this->configPath = cp;
    this->logLevel = ll;
}

FlowerSimulator::~FlowerSimulator() {

}

void FlowerSimulator::start() {
    GlobalConfig::loadConfig(this->configPath, this->logLevel);

    // Logger
    pid_t loggerPid = fork();

    if (loggerPid == 0) {
        {
            Logger logger;
            logger.start();
        }
        exit(0);
    }

    LogPipe logPipe(LOG_WRITE, E_SIMULATOR);
    // *****************

    // Producers
    pid_t producerManagerPid = fork();

    if (producerManagerPid == 0) {
        {
            ProducersManager producersManager;
            producersManager.start();
        }
        exit(0);
    }

    FlowerProtocol producersManagerProtocol(CHANNEL_PRODUCER_MANAGER, NAMED_PIPE_WRITE);
    // *****************


    // Distribution Center
    pid_t distributionManagerPid = fork();

    if (distributionManagerPid == 0) {
        {
            DistributionsManager distributionManager;
            distributionManager.start();
        }
        exit(0);
    }

    FlowerProtocol distributionsManagerProtocol(CHANNEL_DISTRIBUTION_CENTER_MANAGER, NAMED_PIPE_WRITE);
    // *****************


    // Point of sale
    pid_t pointOfSalesManagerPid = fork();

    if (pointOfSalesManagerPid == 0) {
        {
            PointOfSalesManager pointOfSalesManager;
            pointOfSalesManager.start();
        }
        exit(0);
    }

    FlowerProtocol pointOfSalesManagerProtocol(CHANNEL_POINT_OF_SALE_MANAGER, NAMED_PIPE_WRITE);
    // *****************

    // Clients
    pid_t clientsManagerPid = fork();

    if (clientsManagerPid == 0) {
        {
            ClientsManager clientManager;
            clientManager.start();
        }
        exit(0);
    }

    FlowerProtocol clientsManagerProtocol(CHANNEL_CLIENT_MANAGER, NAMED_PIPE_WRITE);
    // *****************


    while (!this->quit) {
        char input[INPUT_BUFFER];
        std::cin.getline(input, INPUT_BUFFER);
        std::string inputString = std::string(input);
        action_t action = FlowerProtocol::parseAction(input);

        switch (action) {
            case ACTION_PAUSE: {
                if (!this->pause) {
                    logPipe << "You selected pause. Let's wait for a while" << END_LINE;
                    producersManagerProtocol.sendAction(ACTION_PAUSE);
                    distributionsManagerProtocol.sendAction(ACTION_PAUSE);
                    pointOfSalesManagerProtocol.sendAction(ACTION_PAUSE);
                    clientsManagerProtocol.sendAction(ACTION_PAUSE);
                    this->pause = true;
                }

                break;
            }

            case ACTION_PRINT_ANALYTICS: {
                logPipe << "You selected print analytics" << END_LINE;
                pointOfSalesManagerProtocol.sendAction(ACTION_PRINT_ANALYTICS);

                break;
            }

            case ACTION_RESUME: {
                if (this->pause) {
                    logPipe << "You selected resume. Let's start again" << END_LINE;
                    producersManagerProtocol.sendAction(ACTION_RESUME);
                    distributionsManagerProtocol.sendAction(ACTION_RESUME);
                    pointOfSalesManagerProtocol.sendAction(ACTION_RESUME);
                    clientsManagerProtocol.sendAction(ACTION_RESUME);
                    this->pause = false;
                }

                break;
            }

            case ACTION_QUIT: {
                logPipe << "You selected quit. Goodbye" << END_LINE;
                producersManagerProtocol.sendAction(ACTION_QUIT);
                distributionsManagerProtocol.sendAction(ACTION_QUIT);
                pointOfSalesManagerProtocol.sendAction(ACTION_QUIT);
                clientsManagerProtocol.sendAction(ACTION_QUIT);
                this->quit = true;
                break;
            }
            default: {
                logPipe << "Unknown action: '" << input << "'" << END_LINE;
                break;
            }
        }
    }

    logPipe << "Simulator ends, waiting for child processes" << END_LINE;

    int producerManagerStatus;
    waitpid(producerManagerPid, &producerManagerStatus, 0);
    logPipe << "Producers manager process " << producerManagerPid << " with status " << producerManagerStatus << END_LINE;

    int distributionCenterManagerStatus;
    waitpid(distributionManagerPid, &distributionCenterManagerStatus, 0);
    logPipe << "Distribution centers manager process " << distributionManagerPid << " with status " << distributionCenterManagerStatus << END_LINE;

    int pointOfSalesManagerStatus;
    waitpid(pointOfSalesManagerPid, &pointOfSalesManagerStatus, 0);
    logPipe << "Point of sales manager process " << pointOfSalesManagerPid << " with status " << pointOfSalesManagerStatus << END_LINE;

    int clientsManagerStatus;
    waitpid(clientsManagerPid, &clientsManagerStatus, 0);
    logPipe << "Client manager process " << clientsManagerPid << " with status " << clientsManagerStatus << END_LINE;

    logPipe.notify(ACTION_QUIT);
    int loggerStatus;
    waitpid(loggerPid, &loggerStatus,0);
    std::cout << "[SIMULATOR] Logger process " << loggerPid << " with status " << loggerStatus << std::endl;

    GlobalConfig::releaseConfig();
}
