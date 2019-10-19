//
// Created by demian on 22/9/19.
//

#include <utils/ConcuMath.h>
#include "Order.h"
#include "utils/GlobalConfig.h"

Order::Order()
{
    numberOfRoses = 0;
    numberOfTulips = 0;
}

Order Order::createOrderByType(order_type type, order_id id)
{
    Order newOrder;
    newOrder.id = id;
    newOrder.type = type;

    newOrder.updateNameFromType();

    GlobalConfig* config = GlobalConfig::getConfig();

    switch(type) {
        case E_ORDER_LOCAL :
        {
            newOrder.numberOfTulips = ConcuMath::getRandomInt(config->localOrderMinTulips, config->localOrderMaxTulips);
            newOrder.numberOfRoses = ConcuMath::getRandomInt(config->localOrderMinRoses, config->localOrderMaxRoses);
            break;
        }

        // Internet order will be processed by the point of sale
    }

    return newOrder;
}

void Order::serialize(Serializer &serializer) {
    serializer << id;
    serializer << type;
    serializer << numberOfRoses;
    serializer << numberOfTulips;

    if(serializer.isReading())
    {
        updateNameFromType();
    }
}

std::string Order::describe(void) const {
    std::stringstream ss;
    ss << "Type: " << this->orderName << "\t" << "ID: " << this->id << "\t" << "Roses: " << this->numberOfRoses << "\t" << "Tulips: " << this->numberOfTulips;
    return ss.str();
}

void Order::updateNameFromType() {
    switch(type)
    {
        case E_ORDER_INTERNET :
            orderName = "Internet";
            break;
        case E_ORDER_LOCAL :
            orderName = "Local";
            break;
    }
}
