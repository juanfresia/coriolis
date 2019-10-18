#ifndef TYPES_H
#define TYPES_H

#include <vector>

// Flower
typedef enum {
    FLOWER_ROSE = 1,
    FLOWER_TULIP = 2
} flower_t;

typedef int flower_id;
//


// Protocol
typedef char event_t;
typedef char action_t;
//


// Producer
typedef int producer_id;
//

// Distribution
typedef int distribution_id;
//

// Point of sale
typedef int point_of_sale_id;

// Order
typedef int order_id;

typedef struct {
    std::string buyer;
    unsigned int roses;
    unsigned int tulips;
} internet_order_t;

typedef struct {
    int id;
    std::string name;
    std::vector<internet_order_t> internetOrders;
} point_of_sale_cfg_t;
//


// Utils
typedef enum {
    E_SIMULATOR,
    E_PRODUCER_MANAGER,
    E_PRODUCER,
    E_DISTRIBUTION_MANAGER,
    E_DISTRIBUTION_CENTER,
    E_POINT_OF_SALE,
    E_POINT_OF_SALES_MANAGER,
    E_ANALYTICS,
    E_LOGGER,
    E_CLIENT_MANAGER,
    E_CLIENT
} entity_t;
//


// Pipes
typedef int descriptor_read;
typedef int descriptor_write;


typedef enum {
    NAMED_PIPE_READ = 1,
    NAMED_PIPE_WRITE = 2,
} named_pipe_type_t ;
//

#endif // TYPES_H
