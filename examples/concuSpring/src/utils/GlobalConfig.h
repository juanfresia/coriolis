//
// Created by demian on 8/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_GLOBALCONFIG_H
#define TP1_FIUBA_CONCURRENTE_GLOBALCONFIG_H

#include <string>
#include <vector>
#include "types.h"


class GlobalConfig {

public:
    static void loadConfig(const std::string &, const std::string &);
    static void releaseConfig();
    inline static GlobalConfig* getConfig() { return globalConfig; }

    // Distribution Center Config
    unsigned int maxDistributionCenters;
    unsigned int classifiedFlowersPackageSize;

    // Point of Sale Config
    std::vector<point_of_sale_cfg_t> pointOfSalesConfig;

    // Producers Config
    unsigned int maxFlowerProducers;
    float roseHarvestProbability;
    float failHarvestProbability;
    float secondsToSleepAfterHarvestTry;
    std::string showLog;

    //CLients
    float clientSleepTime;
    float clientFailOrderProbability;
    unsigned int localOrderMaxRoses;
    unsigned int localOrderMinRoses;
    unsigned int localOrderMaxTulips;
    unsigned int localOrderMinTulips;

private:
    GlobalConfig();
    void load(const std::string &, const std::string &);

    static GlobalConfig* globalConfig;
};


#endif //TP1_FIUBA_CONCURRENTE_GLOBALCONFIG_H
