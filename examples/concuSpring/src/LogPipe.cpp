//
// Created by a128537 on 14/9/19.
//

#include <string>
#include <utils/GlobalConfig.h>
#include "LogPipe.h"
#include "utils/utils.h"

LogPipe::LogPipe(log_t type, entity_t entity) :
    protocol(LOG_FIFO_NAME, NAMED_PIPE_WRITE),
    type(type) {

    this->ignore_log = false;
    std::string logConfig = GlobalConfig::getConfig()->showLog;

    switch(entity) {
        case E_SIMULATOR: {
            this->entity =  "SIMULATOR";
            break;
        }
        case E_PRODUCER_MANAGER: {
            if (logConfig != SHOW_PRODUCER_LOGS) ignore_log = true;
            this->entity = "PRODUCER MANAGER";
            break;
        }
        case E_DISTRIBUTION_MANAGER: {
            if (logConfig != SHOW_DISTRIBUTION_LOGS) ignore_log = true;
            this->entity = "DISTRIBUTION MANAGER";
            break;
        }
        case E_DISTRIBUTION_CENTER: {
            if (logConfig != SHOW_DISTRIBUTION_LOGS) ignore_log = true;
            this->entity = "DISTRIBUTION CENTER";
            break;
        }
        case E_PRODUCER: {
            if (logConfig != SHOW_PRODUCER_LOGS) ignore_log = true;
            this->entity = "PRODUCER";
            break;
        }
        case E_POINT_OF_SALE: {
            if (logConfig != SHOW_SALES_LOGS) ignore_log = true;
            this->entity = "POINT OF SALE";
            break;
        }
        case E_POINT_OF_SALES_MANAGER: {
            if (logConfig != SHOW_SALES_LOGS) ignore_log = true;
            this->entity = "POINT OF SALES MANAGER";
            break;
        }
        case E_LOGGER: {
            this->entity = "LOGGER";
            break;
        }
        case E_ANALYTICS: {
            this->entity = "ANALYTICS";
            break;
        }
        case E_CLIENT_MANAGER: {
            this->entity = "CLIENTS MANGER";
            break;
        }
        case E_CLIENT: {
            this->entity = "CLIENT";
            break;
        }

        default: {
            this->entity ="UNKNOWN";
            break;
        }
    }

    if (logConfig == SHOW_ALL_LOGS) ignore_log = false;
}

LogPipe::~LogPipe() {

}

int LogPipe::writeLogPipe(void) {
    if (type != LOG_WRITE) {
        throw "Could not write in read log pipe";
    }
    if (this->ignore_log) return 0;

    std::string slog;
    slog = currentDateTime() + " " + this->entity + ": " + this->construct_message;
    this->construct_message.clear();

    return protocol.sendLog(slog);
}

LogPipe & LogPipe::operator<<(const char * msg) {
    this->construct_message += msg;
    return * this;
}

LogPipe & LogPipe::operator<<(log_concat concat) {
    if (concat == END_LINE) {
        writeLogPipe();
    }

    return * this;
}

LogPipe & LogPipe::operator<<(int integer) {
    this->construct_message += std::to_string(integer);
    return * this;
}

LogPipe & LogPipe::operator<<(unsigned int integer) {
    this->construct_message += std::to_string(integer);
    return * this;
}

LogPipe & LogPipe::operator<<(long unsigned int integer) {
    this->construct_message += std::to_string(integer);
    return * this;
}

LogPipe & LogPipe::operator<<(std::string msg) {
    this->construct_message += msg;
    return * this;
}

int LogPipe::notify(action_t action) {
    this->protocol.sendAction(action);
}

LogPipe &LogPipe::operator<<(const char c) {
    std::string str;
    str = c;
    this->construct_message += str;
    return * this;
}
