//
// Created by ariel on 19/9/19.
//

#ifndef POINT_OF_SALES_MANAGER_H
#define POINT_OF_SALES_MANAGER_H


#include <map>
#include "LogPipe.h"

class PointOfSalesManager {
    private:
        FlowerProtocol protocol;
        LogPipe logPipe;
        LogPipe analyticsPipe;
        unsigned int pointOfSalesAmount;

        std::vector<pid_t> processIds;
        std::map<distribution_id, shared_ptr<Pipe>> pointOfSalesPipesWrite;


        void waitPointOfSalesEnd(void);
        void spawnPointOfSales();
        void sendActionToPointOfSales(action_t);
        void printAnalytics();

        // Analytics;
        unsigned int numberOfRosesSold;
        unsigned int numberOfTulipsSold;
        std::map<producer_id , unsigned int> flowersSoldByProducers;

    public:
        PointOfSalesManager();

        virtual ~PointOfSalesManager();

        void start();
};


#endif // POINT_OF_SALES_MANAGER_H
