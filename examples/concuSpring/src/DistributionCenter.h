#ifndef DISTRIBUTION_CENTER__H
#define DISTRIBUTION_CENTER__H

#include <protocol/FlowerProtocol.h>
#include <string>
#include "LogPipe.h"

class DistributionCenter {
    private:
        unsigned int id;
        unsigned int packagesSize;
        std::string name;
        class Pipe & pipeWithManagerRead;
        FlowerProtocol protocol;
        FlowerProtocol pointOfSaleProtocol;
        LogPipe logPipe;

        // Packages of classified flowers
        std::vector<Flower> roses;
        std::vector<Flower> tulips;

        // Pauses the distribution center waiting for
        // a new action, if the new action
        // is quit, updates the boolean parameter
        void pause(bool *);

        // Classifies a box of flowers, separating them
        // into Tulips and Roses, storing them in the corresponding
        // packages private variables
        void classifyFlowers(std::vector<Flower> &);

        // Delivers classified flowers packages to the
        // point of sale manager process
        void deliverFlowersPackages(void);

        // Delivers the necessary packages for the flowers type
        // passed in the collection parameter
        void deliverFlowersTypePackages(std::vector<Flower> &);

    public:
        DistributionCenter(unsigned int id, std::string name, Pipe &);
        ~DistributionCenter();

        void start();

        static std::string randName(void);
        std::string describe(void) const;
};


#endif // DISTRIBUTION_CENTER__H
