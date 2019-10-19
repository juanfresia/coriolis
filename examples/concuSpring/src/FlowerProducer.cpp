#include <unistd.h>
#include "Concurrentes.h"
#include "FlowerProducer.h"
#include "protocol/Pipe.h"
#include "utils/ConcuMath.h"
#include "utils/GlobalConfig.h"
#include "LogPipe.h"
#include "Flower.h"

// @has_checkpoints

static const char * producersNames[] = {
        "Ariel",
        "Demian",
        "Pablo",
        "Gabriel",
        "Lucia",
        "Sergio",
        "Martin",
        "Silvia",
        "Nancy",
        "Guido",
        "Adeodato",
        "Gonzalo",
        "Gara",
        "Bari",
        "Juan",
        "Mirtha",
        "Cleopatra",
        "Georgina",
        "Bianca",
        "Gustavo"
};

#define PRODUCER_NAMES_AMOUNT 20

FlowerProducer::FlowerProducer(producer_id id, std::string name, Pipe & pr) :
    id(id),
    name(name),
    harvestedFlowers(0),
    pipeWithManagerRead(pr),
    protocol(CHANNEL_PRODUCER_MANAGER, NAMED_PIPE_WRITE),
    logPipe(LOG_WRITE, E_PRODUCER){

}

FlowerProducer::~FlowerProducer() {}

std::string FlowerProducer::getName() const {
    return this->name;
}

std::string FlowerProducer::describe() const {
    std::stringstream ss;
    ss << "(id, " << this->id << ")" << "|";
    ss << "(producer name, " << this->name << ")";
    return ss.str();
}

void FlowerProducer::start(void) {
    float sleepTime = GlobalConfig::getConfig()->secondsToSleepAfterHarvestTry;
    bool quit = false;

    while (!quit) {
        int timeToSleep = ConcuMath::getRandomInt(sleepTime, sleepTime * 2);
        logPipe << this->name << " (ID: " << this->id << ") will try harvest for the next " << timeToSleep << " seconds" << END_LINE;
        sleep(sleepTime);

        try {
            Flower newFlower = this->harvestFlower();
            // @checkpoint prod_make_bouquet this->id newFlower.getFlowerId() newFlower.getFlowerName()

            // Send flower
            this->protocol.sendFlower(newFlower);

            // Wait for manager response
            logPipe << this->name << " (ID: " << this->id << ") waiting for action" << END_LINE;
            action_t action = this->protocol.getAction(this->pipeWithManagerRead);
            logPipe << this->name << " (ID: " << this->id << ") received action: '" << action << "'" << END_LINE;


            switch (action) {
                case ACTION_CONTINUE: {
                    continue;
                }

                case ACTION_PAUSE: {
                    this->pause(&quit);
                    break;
                }

                case ACTION_QUIT: {
                    quit = true;
                    break;
                }

                default: {
                    logPipe << this->name << " (ID: " << this->id << ") does not know action: '" << action << "'" << END_LINE;
                }
            }

        } catch (std::exception exception) {
            continue;
        }

    }

    logPipe << this->name << " (ID: " << this->id << ") will quit" << END_LINE;
    exit(0);
}

void FlowerProducer::pause(bool * quit) {
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

Flower FlowerProducer::harvestFlower() {
    GlobalConfig* Config = GlobalConfig::getConfig();

    const float roseHarvestProbability = Config->roseHarvestProbability;
    const float failHarvestProbability = Config->failHarvestProbability;

    const float failNumber = ConcuMath::getRandomFloat(0.0f, 100.0f);



    // Check for fail
    if (failNumber < failHarvestProbability) {
        logPipe << this->name << " (ID: " << this->id << ") failed harvesting flower" << END_LINE;
        throw std::exception();
    }

    const float flowerNumber = ConcuMath::getRandomFloat(0.0f, 100.0f);

    // Increment harvested flowers
    this->harvestedFlowers++;

    if (flowerNumber < roseHarvestProbability) {
        // Rose
        logPipe << this->name << " (ID: " << this->id << ") harvested a rose" << END_LINE;
        return Flower::createFlowerByType(FLOWER_ROSE, this->id * 10000 + this->harvestedFlowers, this->id);
    } else {
        // Tulip
        logPipe << this->name << " (ID: " << this->id << ") harvested a tulip" << END_LINE;
        return Flower::createFlowerByType(FLOWER_TULIP, this->id * 10000 + this->harvestedFlowers, this->id);
    }
}

std::string FlowerProducer::randName(void) {
    const char * name = producersNames[ConcuMath::getRandomInt(0, PRODUCER_NAMES_AMOUNT - 1)];
    return std::string(name);
}
