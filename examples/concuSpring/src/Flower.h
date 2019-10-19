#ifndef FLOWER__H
#define FLOWER__H

#include <sstream>
#include <cstring>
#include <utils/types.h>


class Flower {

protected:
    flower_id id;
    producer_id producerId;
    flower_t type;
    std::string flowerName;

public:

    virtual ~Flower() {}
    std::string getFlowerName(void) const {
        return this->flowerName;
    };

    inline producer_id getProducerId(void) const {
        return this->producerId;
    }

    inline flower_id getFlowerId(void) const {
        return this->id;
    }

    inline flower_t getType(void) const {
        return this->type;
    }

    static Flower createFlowerByType(flower_t, flower_id flowerId, producer_id producerId);

    std::string describe(void) const;


};

#endif // FLOWER__H

