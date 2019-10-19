#include "Flower.h"

Flower Flower::createFlowerByType(flower_t type, flower_id flowerId, producer_id producerId)
{
    Flower newFlower;
    newFlower.type = type;
    newFlower.id = flowerId;
    newFlower.producerId = producerId ;

    switch(type)
    {
        case FLOWER_TULIP :
            newFlower.flowerName = "Tulip";
            break;
        case FLOWER_ROSE :
            newFlower.flowerName = "Rose";
            break;
    }

    return newFlower;
}

std::string Flower::describe(void) const {
    std::stringstream ss;
    ss << "FLOWER: " << this->flowerName << "\t" << "ID: " << this->id << "\t" << "PRODUCER: " << this->producerId;
    return ss.str();
};
