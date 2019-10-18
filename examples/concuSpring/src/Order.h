//
// Created by demian on 22/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_ORDER_H
#define TP1_FIUBA_CONCURRENTE_ORDER_H

#include <utils/Serializer.h>
#include "Concurrentes.h"
#include "Flower.h"

typedef enum {
    E_ORDER_LOCAL,
    E_ORDER_INTERNET
} order_type;



class Order {

public:

    Order();

    static Order createOrderByType(order_type type, order_id id);

    void serialize(Serializer& serializer);

    std::string describe(void) const;

    inline order_type getOrderType() const { return type; }
    inline order_id getOrderId() const { return id; }
    inline unsigned int getTulips() const { return numberOfTulips; }
    inline unsigned int getRoses() const { return numberOfRoses; }

protected:

    order_type type;
    order_id id;
    std::string orderName;

    unsigned int numberOfRoses;
    unsigned int numberOfTulips;

    void updateNameFromType();

};


#endif //TP1_FIUBA_CONCURRENTE_ORDER_H
