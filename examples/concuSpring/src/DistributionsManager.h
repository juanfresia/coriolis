#ifndef DISTRIBUTIONS_MANAGER_H
#define DISTRIBUTIONS_MANAGER_H

#include <protocol/FlowerProtocol.h>
#include <map>
#include "LogPipe.h"
#include "Concurrentes.h"
#include "utils/types.h"

class DistributionsManager {

public:
    DistributionsManager();

    virtual ~DistributionsManager();

    void start();

private:
    FlowerProtocol protocol;
    LogPipe logPipe;
    unsigned int distributionsCenterAmount;

    std::vector<pid_t> processIds;
    std::map<distribution_id, shared_ptr<Pipe>> centerPipesWrite;


    void waitDistributionsCenterEnd(void);
    void spawnCenters();
    void sendActionToCenters(action_t);
};


#endif // DISTRIBUTIONS_MANAGER_H
