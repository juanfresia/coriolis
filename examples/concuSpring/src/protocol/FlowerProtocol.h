#ifndef FLOWER_PROTOCOL_H
#define FLOWER_PROTOCOL_H

#include <vector>
#include <Flower.h>
#include "NamedPipe.h"
#include "Pipe.h"
#include <utils/MemoryWriter.h>
#include "Order.h"

// Named pipes names
#define CHANNEL_PRODUCER_MANAGER "ch_p_m"
#define CHANNEL_DISTRIBUTION_CENTER_MANAGER "ch_dc_m"
#define CHANNEL_POINT_OF_SALE_MANAGER "ch_pofs_m"
#define CHANNEL_CLIENT_MANAGER "ch_client_m"

#define EVENT_USER 'E'
#define EVENT_SIMULATOR 'S'
#define EVENT_ANALYTIC 'A'
#define EVENT_BOX 'B'
#define EVENT_CLASSIFIED_PACKAGE 'P'
#define EVENT_BUY_ORDER 'O'
#define EVENT_LOG 'L'

#define ACTION_QUIT 'q'
#define ACTION_PAUSE 'p'
#define ACTION_RESUME 'r'
#define ACTION_CONTINUE 'c'
#define ACTION_PRINT_ANALYTICS 'a'



class FlowerProtocol {
    private:
        class NamedPipe namedPipe;

        flower_id getFlowerId(void) const;
        flower_t getFlowerType(void) const;

        // Serialize the Flower collection with the Memory Writer
        void serializeFlowers(const std::vector<Flower> &, MemoryWriter &);

        // Deserialize the flower collection in the buffer
        // TODO: Change copy return
        std::vector<Flower> deserializeFlowers(uint8_t *, size_t) const;



    public:
        FlowerProtocol(const std::string, const named_pipe_type_t);
        virtual ~FlowerProtocol();

        // Reads type of event from the current named pipe
        event_t getEventType(void) const;

        // Reads type of event from the unnamed pipe
        event_t getEventType(Pipe &) const;

        // Reads type of action from the current named pipe
        action_t getAction(void) const;

        // Reads type of action from the pipe
        action_t getAction(Pipe &) const;

        // Parses user input string to a action_t type
        static action_t parseAction(std::string);

        // Send action_t to the current named namedPipe
        void sendAction(action_t) const;

        // Send action_t to the unnamed pipe passed
        void sendAction(action_t, Pipe &) const;

        // Send action_t to the unnamed pipe passed
        void sendActionWithHeaderEvent(action_t, Pipe &) const;

        // Reads the worker ID from the current named pipe
        unsigned int getWorkerId(void) const;

        // Reads the flower parameters and creates the
        // corresponding flower (use copy constructor)
        // TODO: Optimize with move constructor
        class Flower receiveFlower(void) const;

        // Sends the flower to the current named pipe
        void sendFlower(Flower &);

        // Sends the flower to the current analytics
        void sendFlowerAnalytics(const Flower &);

        // Sends the box to the current named pipe
        void sendFlowersBox(const std::vector<Flower> &flowers);

        // Sends the classified flowers package to the current named pipe
        void sendClassifiedFlowersPackage(const std::vector<Flower> &flowers, distribution_id);

        // Sends the classified flowers package to the unnamed pipe
        void sendClassifiedFlowersPackage(const std::vector<Flower> &flowers, distribution_id, Pipe &);

        // Sends the box to the unnamed pipe
        void sendFlowersBox(const std::vector<Flower> &flowers, Pipe &pipe);

        // Sends a buy order
        void sendBuyOrder(Order& order);

        // Sends a buy order to the unnamed pipe
        void sendBuyOrder(Order& order, Pipe &pipe);

        Order receiveOrder();

        Order receiveOrder(Pipe& pipe);

        // Reads the box from the named pipe
        std::vector<Flower> receiveFlowersBox(void);

        // Reads the box from the unnamed pipe
        std::vector<Flower> receiveFlowersBox(Pipe &pipe);

        // Reads the package from the named pipe
        std::vector<Flower> receiveClassifiedFlowersPackage(distribution_id *);

        // Reads the package from the unnamed pipe
        std::vector<Flower> receiveClassifiedFlowersPackage(distribution_id *, Pipe &);

        int sendLog(std::string msg);

        std::string receiveLog();
};


#endif // FLOWER_PROTOCOL_H
