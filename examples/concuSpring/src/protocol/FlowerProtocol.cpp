#include <cstring>
#include <iostream>
#include <utils/MemoryWriter.h>
#include <netinet/in.h>
#include <utils/MemoryReader.h>
#include <FlowerProducer.h>
#include "FlowerProtocol.h"
#include "NamedPipe.h"
#include "Flower.h"

#define ACTION_QUIT_STR "q"
#define ACTION_PAUSE_STR "p"
#define ACTION_RESUME_STR "r"
#define ACTION_ANALYTICS_STR "a"

FlowerProtocol::FlowerProtocol(const std::string path, named_pipe_type_t mode) :
        namedPipe(path, mode) {

}

FlowerProtocol::~FlowerProtocol() {

}

action_t FlowerProtocol::parseAction(std::string input) {
    if (input == ACTION_QUIT_STR) return ACTION_QUIT;
    if (input == ACTION_PAUSE_STR) return ACTION_PAUSE;
    if (input == ACTION_RESUME_STR) return ACTION_RESUME;
    if (input == ACTION_ANALYTICS_STR) return ACTION_PRINT_ANALYTICS;

    return -1;
}

event_t FlowerProtocol::getEventType(void) const {
    event_t event;
    uint8_t buff[sizeof(event_t)];
    this->namedPipe.readPipe(buff, sizeof(event_t));
    memcpy(&event, buff, sizeof(event_t));
    return event;
}

event_t FlowerProtocol::getEventType(Pipe & pipe) const {
    event_t event;
    uint8_t buff[sizeof(event_t)];
    pipe.readPipe(buff, sizeof(event_t));
    memcpy(&event, buff, sizeof(event_t));
    return event;
}

action_t FlowerProtocol::getAction(void) const {
    action_t action;
    uint8_t buff[sizeof(action_t)];
    this->namedPipe.readPipe(buff, sizeof(action_t));
    memcpy(&action, buff, sizeof(action_t));
    return action;
}

action_t FlowerProtocol::getAction(Pipe & pipe) const {
    action_t action;
    uint8_t buff[sizeof(action_t)];
    pipe.readPipe(buff, sizeof(action_t));
    memcpy(&action, buff, sizeof(action_t));
    return action;
}

void FlowerProtocol::sendAction(action_t action) const {
    MemoryWriter writer;
    event_t event = EVENT_USER;
    writer << event;
    writer << action;
    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendActionWithHeaderEvent(action_t action, Pipe & unnamedPipe) const {
    MemoryWriter writer;
    event_t event = EVENT_USER;
    writer << event;
    writer << action;
    unnamedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendAction(action_t action, Pipe & unnamedPipe) const {
    MemoryWriter writer;
    writer << action;
    unnamedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

unsigned int FlowerProtocol::getWorkerId(void) const {
    unsigned int workerId;
    uint8_t buff[sizeof(workerId)];
    this->namedPipe.readPipe(buff, sizeof(workerId));
    memcpy(&workerId, buff, sizeof(workerId));
    return workerId;
}

flower_t FlowerProtocol::getFlowerType(void) const {
    flower_t type;
    uint8_t buff[sizeof(flower_t)];
    this->namedPipe.readPipe(buff, sizeof(flower_t));
    memcpy(&type, buff, sizeof(flower_t));
    return (flower_t) type;
}

flower_id FlowerProtocol::getFlowerId(void) const {
    flower_id id;
    uint8_t buff[sizeof(flower_id)];
    this->namedPipe.readPipe(buff, sizeof(flower_id));
    memcpy(&id, buff, sizeof(flower_id));
    return (flower_id) id;
}

Flower FlowerProtocol::receiveFlower(void) const {
    flower_id id = this->getFlowerId();
    producer_id producerId = (producer_id) this->getWorkerId();
    flower_t type = this->getFlowerType();

    return Flower::createFlowerByType(type, id, producerId);
}

void FlowerProtocol::sendFlower(Flower & flower) {
    MemoryWriter writer;
    event_t event = EVENT_SIMULATOR;
    flower_id id = flower.getFlowerId();
    producer_id producerId = flower.getProducerId();
    int type = flower.getType();
    writer << event;
    writer << id;
    writer << producerId;
    writer << type;

    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendFlowerAnalytics(const Flower & flower) {
    MemoryWriter writer;
    event_t event = EVENT_ANALYTIC;
    flower_id id = flower.getFlowerId();
    producer_id producerId = flower.getProducerId();
    int type = flower.getType();
    writer << event;
    writer << id;
    writer << producerId;
    writer << type;

    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

int FlowerProtocol::sendLog(std::string msg) {
    event_t event = EVENT_LOG;
    int log_size = msg.size();

    int bufferSize = sizeof(event_t) + sizeof(int) + msg.size();
    unsigned char buffer[bufferSize];
    unsigned char * index = buffer;

    memcpy(index, &event, sizeof(event_t));
    index += sizeof(event_t);

    memcpy(index, &log_size, sizeof(int));
    index += sizeof(int);

    memcpy(index, msg.c_str(), msg.size());

    return this->namedPipe.writePipe(buffer, bufferSize);
}

std::string FlowerProtocol::receiveLog() {
    int log_size;
    this->namedPipe.readPipe((uint8_t *) &log_size, sizeof(log_size));

    uint8_t buff[log_size];

    this->namedPipe.readPipe(buff, log_size);

    std::string msg;
    msg.assign((const char *) &(buff[0]), log_size);

    return msg;
}

void FlowerProtocol::serializeFlowers(const std::vector<Flower> & flowers, MemoryWriter & writer) {

    MemoryWriter boxWriter;
    size_t elementsAmount = flowers.size();
    boxWriter << elementsAmount;

    for (const Flower & flower: flowers) {
        flower_id id = flower.getFlowerId();
        producer_id producerId = flower.getProducerId();
        flower_t type = flower.getType();

        boxWriter << id;
        boxWriter << producerId;
        boxWriter << type;
    }

    // serialize the collection size so we can read all the bytes together
    size_t collectionSize = boxWriter.getBufferSize();
    writer << collectionSize;
    writer.serialize(boxWriter.getBuffer(), boxWriter.getBufferSize());
}


std::vector<Flower> FlowerProtocol::deserializeFlowers(uint8_t * buffer, size_t size) const {
    MemoryReader reader(buffer, size);
    std::vector<Flower> flowers;

    size_t collectionElements = 0;
    reader << collectionElements;

    for (size_t i = 0; i < collectionElements; i++) {
        flower_id id = 0;
        producer_id producerId = 0;
        flower_t type = FLOWER_ROSE;

        reader << id;
        reader << producerId;
        reader << type;

        Flower newFlower = Flower::createFlowerByType(type, id, producerId);
        flowers.push_back(newFlower);
    }

    return flowers;
}

void FlowerProtocol::sendFlowersBox(const std::vector<Flower> & flowers) {
    MemoryWriter writer;
    event_t event = EVENT_BOX;
    writer << event;

    this->serializeFlowers(flowers, writer);

    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendFlowersBox(const std::vector<Flower> & flowers, Pipe & pipe) {
    MemoryWriter writer;
    event_t event = EVENT_BOX;
    writer << event;

    this->serializeFlowers(flowers, writer);
    pipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

std::vector<Flower> FlowerProtocol::receiveFlowersBox(void) {
    // read the box size
    uint8_t buff[sizeof(size_t)];
    this->namedPipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the box
    this->namedPipe.readPipe(collectionBuffer, size);

    // process the box
    return this->deserializeFlowers(collectionBuffer, size);
}

std::vector<Flower> FlowerProtocol::receiveFlowersBox(Pipe & pipe) {
    // read the box size
    uint8_t buff[sizeof(size_t)];
    pipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the box
    pipe.readPipe(collectionBuffer, size);

    // process the box
    return this->deserializeFlowers(collectionBuffer, size);
}

void FlowerProtocol::sendClassifiedFlowersPackage(const std::vector<Flower> &flowers, distribution_id distributionId) {
    MemoryWriter writer;
    event_t event = EVENT_CLASSIFIED_PACKAGE;
    writer << event;
    writer << distributionId;

    this->serializeFlowers(flowers, writer);

    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendClassifiedFlowersPackage(const std::vector<Flower> & flowers, distribution_id did, Pipe & unnamedPipe) {
    MemoryWriter writer;
    event_t event = EVENT_CLASSIFIED_PACKAGE;
    writer << event;
    writer << did;

    this->serializeFlowers(flowers, writer);

    unnamedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

std::vector<Flower> FlowerProtocol::receiveClassifiedFlowersPackage(distribution_id * distributionId) {
    uint8_t distIdBuff[sizeof(distribution_id)];
    this->namedPipe.readPipe(distIdBuff, sizeof(distribution_id));

    distribution_id distributionIdValue;
    memcpy(&distributionIdValue, distIdBuff, sizeof(distribution_id));
    *distributionId = distributionIdValue;

    // read the package size
    uint8_t buff[sizeof(size_t)];
    this->namedPipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the package
    this->namedPipe.readPipe(collectionBuffer, size);

    // process the package
    return this->deserializeFlowers(collectionBuffer, size);
}

std::vector<Flower> FlowerProtocol::receiveClassifiedFlowersPackage(distribution_id * id, Pipe & unnamedPipe) {
    uint8_t distIdBuff[sizeof(distribution_id)];
    unnamedPipe.readPipe(distIdBuff, sizeof(distribution_id));

    distribution_id distributionIdValue;
    memcpy(&distributionIdValue, distIdBuff, sizeof(distribution_id));
    *id = distributionIdValue;

    // read the package size
    uint8_t buff[sizeof(size_t)];
    unnamedPipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the package
    unnamedPipe.readPipe(collectionBuffer, size);

    // process the package
    return this->deserializeFlowers(collectionBuffer, size);
}

void FlowerProtocol::sendBuyOrder(Order &order) {
    MemoryWriter writer;
    event_t event = EVENT_BUY_ORDER;
    writer << event;

    MemoryWriter orderWriter;
    order.serialize(orderWriter);

    size_t orderSize = orderWriter.getBufferSize();
    writer << orderSize;

    writer.serialize(orderWriter.getBuffer(), orderSize);

    this->namedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

void FlowerProtocol::sendBuyOrder(Order &order, Pipe &unnamedPipe) {
    MemoryWriter writer;
    event_t event = EVENT_BUY_ORDER;
    writer << event;

    MemoryWriter orderWriter;
    order.serialize(orderWriter);

    size_t orderSize = orderWriter.getBufferSize();
    writer << orderSize;

    writer.serialize(orderWriter.getBuffer(), orderSize);

    unnamedPipe.writePipe(writer.getBuffer(), writer.getBufferSize());
}

Order FlowerProtocol::receiveOrder() {
    // read the order size
    uint8_t buff[sizeof(size_t)];
    this->namedPipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the order
    this->namedPipe.readPipe(collectionBuffer, size);

    MemoryReader reader(collectionBuffer, size);
    Order newOrder;

    newOrder.serialize(reader);

    return newOrder;
}

Order FlowerProtocol::receiveOrder(Pipe &pipe) {

    // read the order size
    uint8_t buff[sizeof(size_t)];
    pipe.readPipe(buff, sizeof(size_t));

    size_t size = 0;
    memcpy(&size, buff, sizeof(size_t));

    // feature available since c++11
    uint8_t collectionBuffer[size];
    // read the order
    pipe.readPipe(collectionBuffer, size);

    MemoryReader reader(collectionBuffer, size);
    Order newOrder;

    newOrder.serialize(reader);

    return newOrder;
}







