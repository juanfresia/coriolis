#include <sstream>
#include <utils/ConcuMath.h>
#include <assert.h>
#include <utils/GlobalConfig.h>
#include "DistributionCenter.h"
#include "Flower.h"

// @has_checkpoints

static const char * centersNames[] = {
    "Fiuba",
    "Disney",
    "Demacia",
    "Noxus",
    "Eldia",
    "Mare",
    "Ionia",
    "Muy lejano",
    "La salada",
    "Atlantis",
    "Chile"
};

#define CENTER_NAMES_AMOUNT 11

DistributionCenter::DistributionCenter(unsigned int id, std::string name, Pipe & pr) :
    id(id),
    name(name),
    pipeWithManagerRead(pr),
    protocol(CHANNEL_DISTRIBUTION_CENTER_MANAGER, NAMED_PIPE_WRITE),
    pointOfSaleProtocol(CHANNEL_POINT_OF_SALE_MANAGER, NAMED_PIPE_WRITE),
    logPipe(LOG_WRITE, E_DISTRIBUTION_CENTER) {


    this->packagesSize = GlobalConfig::getConfig()->classifiedFlowersPackageSize;

}

DistributionCenter::~DistributionCenter() {}

void DistributionCenter::start() {

    bool quit = false;

    while (!quit) {
        // Wait for manager response
        logPipe << this->describe() << " waiting for event" << END_LINE;
        event_t event = this->protocol.getEventType(this->pipeWithManagerRead);
        logPipe << this->describe() << " received event: '" << event << "'" << END_LINE;

        if (event == EVENT_USER) {
            logPipe << this->describe() << " received user event, waiting for user action" << END_LINE;
            action_t action = this->protocol.getAction(this->pipeWithManagerRead);
            logPipe << this->describe() << " received action: '" << action << "'" << END_LINE;

            switch (action) {
                case ACTION_CONTINUE: {
                    continue;
                }

                case ACTION_PAUSE: {
                    this->pause(&quit);
                    break;
                }

                case ACTION_RESUME: {
                    // Ignore if it is not paused
                    break;
                }

                case ACTION_QUIT: {
                    quit = true;
                    break;
                }

                default: {
                    logPipe << this->name << " (ID: " << this->id << ") does not know action: '" << action << "'"
                            << END_LINE;
                }
            }
        }

        if (event == EVENT_BOX) {
            std::vector<Flower> flowerBox = this->protocol.receiveFlowersBox(this->pipeWithManagerRead);
            logPipe << this->describe() << " received box with: " << flowerBox.size() << " number of flowers" << END_LINE;
            // @checkpoint dc_receive_box this->id flowerBox.front().getFlowerId()

            this->classifyFlowers(flowerBox);
            this->deliverFlowersPackages();
        }

    }

    logPipe << this->describe() << " will quit" << END_LINE;
    exit(0);
}


std::string DistributionCenter::describe() const {
    std::stringstream ss;
    ss << this->name << " (ID: " << this->id << ")";
    return ss.str();
}

std::string DistributionCenter::randName(void) {
    const char * name = centersNames[ConcuMath::getRandomInt(0, CENTER_NAMES_AMOUNT - 1)];
    return std::string(name);
}

void DistributionCenter::pause(bool * quit) {
    logPipe << this->name << " (ID: " << this->id << ") is paused" << END_LINE;
    action_t action = this->protocol.getAction(this->pipeWithManagerRead);

    switch (action) {
        case ACTION_RESUME: {
            logPipe << this->name << " (ID: " << this->id << ") will resume" << END_LINE;
            return;
        }

        case ACTION_QUIT: {
            *quit = true;
            return;
        }

        default:
            this->pause(quit);
    }
}

void DistributionCenter::classifyFlowers(std::vector<Flower> & box) {
    for (Flower & flower: box) {

        flower_t type = flower.getType();

        switch (type) {
            case FLOWER_ROSE:
                this->roses.push_back(flower);
                // @checkpoint dc_unbox_bouquet this->id flower.getFlowerId() box.front().getFlowerId() flower.getFlowerName()
                break;
            case FLOWER_TULIP:
                this->tulips.push_back(flower);
                // @checkpoint dc_unbox_bouquet this->id flower.getFlowerId() box.front().getFlowerId() flower.getFlowerName()
                break;
            default:
                logPipe << this->describe() << " could not classify flower of type: " << type << END_LINE;
        }
    }

    logPipe << this->describe() << " finish classifying the received box" << END_LINE;
    logPipe
        << this->describe()
        << " now has "
        << this->roses.size()
        << " roses and "
        << this->tulips.size()
        << " tulips" << END_LINE;
}

void DistributionCenter::deliverFlowersPackages(void) {
    logPipe
        << this->describe()
        << " will deliver classified flowers packages"
        << END_LINE;

    this->deliverFlowersTypePackages(this->roses);
    this->deliverFlowersTypePackages(this->tulips);

    logPipe
        << this->describe()
        << " finish delivering classified flowers packages"
        << END_LINE;

    logPipe
        << this->describe()
        << " after delivering has "
        << this->roses.size()
        << " roses and "
        << this->tulips.size()
        << " tulips" << END_LINE;
}

void DistributionCenter::deliverFlowersTypePackages(std::vector<Flower> & flowersType) {


    while (flowersType.size() >= this->packagesSize) {
        // Creates "package" with last "package size" elements
        std::vector<Flower> package(flowersType.end() - this->packagesSize, flowersType.end());
        for (Flower & flower: package) {
			// @checkpoint dc_package_bouquet this->id flower.getFlowerId() package.front().getFlowerId() package.front().getFlowerName()
		}
        assert(package.size() == this->packagesSize);

        // Send to point of sale manager
        this->pointOfSaleProtocol.sendClassifiedFlowersPackage(package, this->id);

        // Removes last "package size" elements
        flowersType.resize(flowersType.size() - this->packagesSize);
    }
}
