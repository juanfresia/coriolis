#ifndef FLOWER_PRODUCER__H
#define FLOWER_PRODUCER__H

#include <string>
#include <utils/types.h>
#include <protocol/FlowerProtocol.h>
#include "Concurrentes.h"
#include "LogPipe.h"

class Flower;
class FlowerProtocol;

class FlowerProducer {
    private:
        producer_id id;
        std::string name;
        class Pipe & pipeWithManagerRead;
        LogPipe logPipe;
        FlowerProtocol protocol;
        unsigned int harvestedFlowers;

        // Pauses the producer waiting for
        // a new action, if the new action
        // is quit, updates the boolean parameter
        void pause(bool *);

        Flower harvestFlower();

    public:
        FlowerProducer(producer_id id, std::string name, Pipe &);
        ~FlowerProducer();

        static std::string randName(void);

        std::string getName(void) const;
        std::string describe(void) const;

        void start(void);
};


#endif // FLOWER_PRODUCER__H
