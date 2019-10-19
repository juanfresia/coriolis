//
// Created by a128537 on 14/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_LOGGER_H
#define TP1_FIUBA_CONCURRENTE_LOGGER_H

#include <protocol/FlowerProtocol.h>

class Logger {
private:
    FlowerProtocol protocol;
    std::ostream & out_stream;

public:
    Logger();

    virtual ~Logger();

    void start();
};


#endif //TP1_FIUBA_CONCURRENTE_LOGGER_H
