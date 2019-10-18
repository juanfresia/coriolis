#include "GlobalConfig.h"
#include <json/json.h>
#include "../Concurrentes.h"

GlobalConfig* GlobalConfig::globalConfig = nullptr;

void GlobalConfig::loadConfig(const std::string & configPath, const std::string & logLevel) {

    if(isNotValid(globalConfig))
    {
        globalConfig = new GlobalConfig();
        globalConfig->load(configPath, logLevel);
    }
}

void GlobalConfig::releaseConfig() {
    if(isValid(globalConfig))
    {
        delete globalConfig;
    }
}

GlobalConfig::GlobalConfig() {
    maxFlowerProducers = 1;
    maxDistributionCenters = 1;

    roseHarvestProbability = 50.0f;
    failHarvestProbability = 0.0f;
    secondsToSleepAfterHarvestTry = 1.0f;
}

void GlobalConfig::load(const std::string & configPath, const std::string & logLevel) {
    // Create json object
    Json::Value root;

    // Read from file
    try {
        std::ifstream config_doc(configPath, std::ifstream::binary);

        // Parse file with the json object
        config_doc >> root;
        // Close file
        config_doc.close();
    } catch (std::exception e) {
        std::cerr << "Could not open config file " << e.what() << std::endl;
        exit(0);
    }

    // get json values from the root

    // Distribution centers
    maxDistributionCenters = root["MaxDistributionCenters"].asUInt();
    classifiedFlowersPackageSize = root["ClassifiedFlowersPackageSize"].asUInt();

    // Point of sale
    const Json::Value pointsOfSales = root["pointsOfSales"];
    for (int i = 0 ; i < pointsOfSales.size() ; i++) {
        Json::Value pofs = pointsOfSales[i];
        point_of_sale_cfg_t pofsConfig;

        pofsConfig.id = pofs["id"].asUInt();
        pofsConfig.name = pofs["name"].asString();
        const Json::Value internetOrders = pofs["internetOrders"];
        for (int i = 0 ; i < internetOrders.size() ; i++) {
            Json::Value internetOrder = internetOrders[i];
            internet_order_t order;
            order.buyer = internetOrder["buyer"].asString();
            order.roses = internetOrder["roses"].asUInt();
            order.tulips = internetOrder["tulips"].asUInt();
            pofsConfig.internetOrders.push_back(order);
        }

        this->pointOfSalesConfig.push_back(pofsConfig);
    }


    // Producers
    maxFlowerProducers = root["MaxFlowerProducers"].asUInt();
    roseHarvestProbability = root["RoseHarvestProbability"].asFloat();
    failHarvestProbability = root["FailHarvestProbability"].asFloat();
    secondsToSleepAfterHarvestTry = root["SecondsToSleepAfterHarvestTry"].asFloat();

    // Clients
    clientSleepTime = root["clientSleepTime"].asFloat();
    clientFailOrderProbability = root["clientFailOrderProbability"].asFloat();

    localOrderMaxRoses = root["localOrderMaxRoses"].asUInt();
    localOrderMinRoses = root["localOrderMinRoses"].asUInt();
    localOrderMaxTulips = root ["localOrderMaxTulips"].asUInt();
    localOrderMinTulips = root["localOrderMinTulips"].asUInt();

    // Log options
    showLog = logLevel;
}
