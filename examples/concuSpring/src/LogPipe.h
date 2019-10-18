//
// Created by a128537 on 14/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_LOGPIPE_H
#define TP1_FIUBA_CONCURRENTE_LOGPIPE_H

#include <string>
#include <protocol/NamedPipe.h>
#include <protocol/FlowerProtocol.h>

#define LOG_FIFO_NAME "LOG_FIFO"
#define SHOW_ALL_LOGS "A"
#define SHOW_PRODUCER_LOGS "P"
#define SHOW_DISTRIBUTION_LOGS "D"
#define SHOW_SALES_LOGS "S"

typedef enum {
    LOG_READ = NAMED_PIPE_READ,
    LOG_WRITE = NAMED_PIPE_WRITE
} log_t;

typedef enum {
    END_LINE
} log_concat;


class LogPipe {
private:
    FlowerProtocol protocol;
    std::string entity;
    log_t type;
    std::string construct_message;
    bool ignore_log;

public:
    LogPipe(log_t, entity_t);

    int writeLogPipe(void);
    int notify(action_t);

    LogPipe & operator<<(std::string);
    LogPipe & operator<<(int);
    LogPipe & operator<<(unsigned int);
    LogPipe & operator<<(long unsigned int);
    LogPipe & operator<<(const char *);
    LogPipe & operator<<(const char);
    LogPipe & operator<<(log_concat);

    virtual ~LogPipe();

};

#endif //TP1_FIUBA_CONCURRENTE_LOGPIPE_H
