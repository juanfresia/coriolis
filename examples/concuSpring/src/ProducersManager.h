#ifndef PRODUCERS_MANAGER_H
#define PRODUCERS_MANAGER_H

#include "Concurrentes.h"
#include "protocol/Pipe.h"
#include "FlowerProducer.h"
#include "LogPipe.h"
#include <vector>
#include <map>
#include <protocol/FlowerProtocol.h>

#define MAX_BOX_SIZE 10

class Pipe;

struct producer_stats {
    unsigned int flowersProduced;
    unsigned int rosesProduced;
    unsigned int tulipProduced;
    producer_stats() :
        flowersProduced(0),
        rosesProduced(0),
        tulipProduced(0) {}
};

typedef struct producer_stats producer_stats_t;

class ProducersManager {
    private:
        std::vector<pid_t> processIds;
        std::map<producer_id, shared_ptr<Pipe>> producersPipesWrite;
        std::map<producer_id, std::vector<Flower>> producersFlowerBoxes;
        std::map<producer_id, producer_stats_t> producersStats;

        FlowerProtocol protocol;
        // To send flower box to distribution centers
        FlowerProtocol distributionProtocol;
        LogPipe logPipe;

        void waitProducersEnd(void);
        void spawnProducers(void);
        void sendActionToProducers(action_t);

        // Update producer counters and current box
        void updateProducer(producer_id, Flower &);

        // Clean the box of the producer
        void clearProducerBox(std::vector<Flower> &box);

    public:
        ProducersManager();

        virtual ~ProducersManager();

        void start();
};
#endif // PRODUCERS_MANAGER_H
