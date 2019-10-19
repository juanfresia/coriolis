#ifndef POINT_OF_SALE__H
#define POINT_OF_SALE__H


#include <string>
#include <utils/types.h>
#include <map>
#include "LogPipe.h"

class PointOfSale {
    private:
        unsigned int id;
        std::string name;
        class Pipe & pipeWithManagerRead;
        FlowerProtocol protocol;
        LogPipe logPipe;

        // Internet orders
        std::vector<internet_order_t> orders;

        // Stocks
        std::vector<Flower> rosesStock;
        std::vector<Flower> tulipsStock;

        // Pauses the point of sale waiting for
        // a new action, if the new action
        // is quit, updates the boolean parameter
        void pause(bool *);

        // Pre: package is not empty it has at least one flower
        // Pos: update the corresponding stock of the point of sale
        void updateStocks(std::vector<Flower> & package);

        // Delivers internet orders to the bicycle system if there is any
        // and if there is enough stock. Makes the corresponding invoice
        void deliverInternetOrders(void);

        void deliverLocalOrder(const Order&);

        // Makes an invoice for the corresponding buyer
        // with the flowers passes by parameters
        std::string makeInvoice(std::string buyer, const std::vector<Flower> & roses, const std::vector<Flower> & tulips);

    public:
        PointOfSale(unsigned int id, std::string name, Pipe & pr, std::vector<internet_order_t>);
        ~PointOfSale();

        std::string describe(void) const;
        static std::string randName(void);

        void start();
};


#endif // POINT_OF_SALE__H
