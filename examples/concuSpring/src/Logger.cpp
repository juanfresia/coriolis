//
// Created by a128537 on 14/9/19.
//

#include <iostream>
#include "Logger.h"
#include "utils/types.h"
#include "LogPipe.h"

Logger::Logger() :
protocol(LOG_FIFO_NAME, NAMED_PIPE_READ),
out_stream(std::cout) {

}

Logger::~Logger() {

};

void Logger::start() {
    bool quit = false;

    while (!quit) {
        event_t event = this->protocol.getEventType();

        if (event == EVENT_USER) {
            action_t action = this->protocol.getAction();

            switch (action) {
                case ACTION_QUIT: {
                    std::cout << "[LOGGER] Action Quit" << std::endl;
                    quit = true;
                    continue;
                }

                default: {
                    std::cout << "[LOGGER] Don't know action: " << action << std::endl;
                    break;
                }
            }
        }

        if (event == EVENT_LOG) {
            std::string sLog = this->protocol.receiveLog();
            out_stream << sLog << std::endl;
        }
    }

    return;
}