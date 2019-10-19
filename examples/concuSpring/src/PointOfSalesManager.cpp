#include <utils/GlobalConfig.h>
#include <utils/ConcuMath.h>
#include "PointOfSalesManager.h"
#include "DistributionCenter.h"
#include "PointOfSale.h"

// @has_checkpoints

PointOfSalesManager::PointOfSalesManager() :
    protocol(CHANNEL_POINT_OF_SALE_MANAGER, NAMED_PIPE_READ),
    logPipe(LOG_WRITE, E_POINT_OF_SALES_MANAGER),
    analyticsPipe(LOG_WRITE, E_ANALYTICS){

    numberOfRosesSold = 0;
    numberOfTulipsSold = 0;
}

PointOfSalesManager::~PointOfSalesManager() {
    logPipe << "Destructor" << END_LINE;
    this->waitPointOfSalesEnd();
}

void PointOfSalesManager::waitPointOfSalesEnd(void) {
    // Wait for child process
    for (const pid_t processId: this->processIds) {
        int childResult;
        waitpid(processId, &childResult, 0);
        logPipe << "Point of sale process " << processId << " finished with " << childResult << END_LINE;
    }
}

void PointOfSalesManager::start() {
    this->spawnPointOfSales();
    bool quit = false;
    bool pause = false;

    std::string msg;

    while (!quit) {
        logPipe << "Waiting for event." << END_LINE;
        event_t event = this->protocol.getEventType();
        logPipe << "Received event " << event << END_LINE;

        if (event == EVENT_USER) {
            action_t action = this->protocol.getAction();

            switch (action) {
                case ACTION_QUIT: {
                    logPipe << "Action Quit Received" << END_LINE;
                    this->sendActionToPointOfSales(action);
                    quit = true;
                    break;
                }

                case ACTION_PAUSE: {
                    if (!pause) {
                        logPipe << "Action Pause Received" << END_LINE;
                        pause = true;
                        this->sendActionToPointOfSales(action);
                        break;
                    }
                }

                case ACTION_RESUME: {
                    if (pause) {
                        logPipe << "Action Resume Received" << END_LINE;
                        pause = false;
                        this->sendActionToPointOfSales(action);
                        break;
                    }
                }

                case ACTION_PRINT_ANALYTICS: {
                    this->printAnalytics();
                    break;
                }

                default: {
                    logPipe << "Don't know action: " << action << END_LINE;
                }
            }
        }

        if (event == EVENT_CLASSIFIED_PACKAGE) {
            distribution_id distributionId;
            std::vector<Flower> package = this->protocol.receiveClassifiedFlowersPackage(&distributionId);
            logPipe << "Received a classified flowers package from distribution center with ID: " << distributionId << END_LINE;

            if (pause) continue;

            point_of_sale_id randomPofsId = ConcuMath::getRandomInt(1, this->pointOfSalesAmount);
            shared_ptr<Pipe> pipeWrite = this->pointOfSalesPipesWrite[randomPofsId];
            // @checkpoint dc_send_package distributionId randomPofsId package.front().getFlowerId() package.front().getFlowerName()
            protocol.sendClassifiedFlowersPackage(package, distributionId, *pipeWrite);
            logPipe << "Finish sending package to random point of sale - ID: " << randomPofsId << END_LINE;

        }

        if (event == EVENT_BUY_ORDER) {

            Order order = this->protocol.receiveOrder();
            logPipe << "Received a buy order from client: " << order.describe() << END_LINE;

            if (pause) continue;

            point_of_sale_id randomPofsId = ConcuMath::getRandomInt(1, this->pointOfSalesAmount);
            shared_ptr<Pipe> pipeWrite = this->pointOfSalesPipesWrite[randomPofsId];
            protocol.sendBuyOrder(order, *pipeWrite);
            logPipe << "Finish sending the buy order to random point of sale - ID: " << randomPofsId << END_LINE;
            // @checkpoint customer_make_order order.getOrderId() order.getRoses() order.getTulips() randomPofsId
        }

        if (event == EVENT_ANALYTIC) {
            Flower analyticFlower = this->protocol.receiveFlower();
            analyticsPipe << "Received new flower: " << analyticFlower.describe() << END_LINE;

            switch (analyticFlower.getType())
            {
                case FLOWER_TULIP:
                {
                    numberOfTulipsSold++;
                    break;
                }
                case FLOWER_ROSE:
                {
                    numberOfRosesSold++;
                    break;
                }
            }

            producer_id prodId = analyticFlower.getProducerId();
            if(flowersSoldByProducers.count(prodId) > 0)
            {
                flowersSoldByProducers[prodId]++;
            } else {
                flowersSoldByProducers[prodId] = 1;
            }
        }
    }

    return;
}

void PointOfSalesManager::printAnalytics() {
    analyticsPipe << "-- Printing analytics --" << END_LINE;

    if(numberOfTulipsSold > numberOfRosesSold) {
        analyticsPipe << "Tulip has more sales than Roses with: " << numberOfTulipsSold << " over " <<numberOfRosesSold << END_LINE;
    }
    else if(numberOfRosesSold > numberOfTulipsSold) {
        analyticsPipe << "Roses has more sales than Tulip with: " << numberOfRosesSold << " over " <<numberOfTulipsSold << END_LINE;
    }
    else {
        analyticsPipe << "Roses and Tulip has the same sales: " << numberOfRosesSold << END_LINE;
    }

    producer_id producerId = 0;
    unsigned int flowersSold = 0;

    std::map<producer_id , unsigned int>::iterator it;
    for (it = flowersSoldByProducers.begin(); it != flowersSoldByProducers.end(); it++)
    {
        if(it->second > flowersSold)
        {
            flowersSold = it->second;
            producerId = it->first;
        }
    }

    analyticsPipe << "Producer with most flowers sold - ID:" << producerId << " with " << flowersSold << " flowers" << END_LINE;
}

void PointOfSalesManager::spawnPointOfSales() {
    std::vector<point_of_sale_cfg_t> & pointOfSalesConfig = GlobalConfig::getConfig()->pointOfSalesConfig;

    logPipe << "I will create " << pointOfSalesConfig.size() << " point of sales" << END_LINE;

    for (const point_of_sale_cfg_t & pofSale: pointOfSalesConfig) {
        shared_ptr<Pipe> pipe = shared_ptr<Pipe>(new Pipe());
        point_of_sale_id pointOfSaleId = pofSale.id;
        this->pointOfSalesPipesWrite[pointOfSaleId] = pipe;

        pid_t pid = fork();

        if (pid == 0) {
            {
                PointOfSale pofs(pointOfSaleId, pofSale.name, *pipe, pofSale.internetOrders);
                logPipe << "I created " << pofs.describe() << " with " << pofSale.internetOrders.size() << " orders" << END_LINE;
                pofs.start();
            }
            exit(0);
        } else {
            this->processIds.push_back(pid);
        }
    }

    logPipe << "Finish creating " << pointOfSalesConfig.size() << " point of sales" << END_LINE;

    this->pointOfSalesAmount = pointOfSalesConfig.size();
}



void PointOfSalesManager::sendActionToPointOfSales(action_t action) {
    std::map<point_of_sale_id , shared_ptr<Pipe>>::iterator it;
    for (it = this->pointOfSalesPipesWrite.begin() ; it != this->pointOfSalesPipesWrite.end() ; ++it) {
        this->protocol.sendActionWithHeaderEvent(action, *it->second);
    }
}
