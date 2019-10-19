#include <getopt.h>
#include <iostream>
#include <LogPipe.h>
#include "ArgumentsProcessor.h"

ArgumentsProcessor::ArgumentsProcessor() {}

ArgumentsProcessor::~ArgumentsProcessor() {}

void ArgumentsProcessor::help() {
    std::cout << "Usage:" << std::endl;
    std::cout << "\t" << "tp1 -h" << std::endl;
    std::cout << "\t" << "tp1 -V" << std::endl;
    std::cout << "\t" << "tp1 -[options]" << std::endl;
    std::cout << std::endl;

    std::cout << "Options:" << std::endl;
    std::cout << "\t" << "-h, --help       Print this information" << std::endl;
    std::cout << "\t" << "-V, --version    Print version and quit" << std::endl;
    std::cout << "\t" << "-c, --config     Sets config file path" << std::endl;
    std::cout << "\t" << "-d, --debug      Sets debug level (default is 'A')" << std::endl;
    std::cout << std::endl;
    std::cout << "Available debug levels:" << std::endl;
    std::cout << "\t" << "A       Logs all" << std::endl;
    std::cout << "\t" << "P       Logs only producers information" << std::endl;
    std::cout << "\t" << "D       Logs only distribution centers information" << std::endl;
    std::cout << "\t" << "S       Logs only points of sales information" << std::endl;
    std::cout << std::endl;

    std::cout << "Examples:" << std::endl;
    std::cout << "\t" << "tp1 --help" << std::endl;
    std::cout << "\t" << "tp1 -V" << std::endl;
    std::cout << "\t" << "tp1 --config ./config/config.json" << std::endl;
    std::cout << "\t" << "tp1 --config ./config/config.json -d P" << std::endl;
}

void ArgumentsProcessor::version() {
    std::cout << "TP 1 - Técnicas de Programación Concurrente I" << std::endl;
    std::cout << "Version: 1.0" << std::endl;
    std::cout << "Contribuitors: ALVAREZ WINDEY Ariel, LOPEZ Demian, ROBLES Gabriel" << std::endl;
}

int ArgumentsProcessor::processArguments(int argc, char **argv, std::string & path, std::string & logLevel) {
    int c;
    static struct option long_options[] = {
            {"version", no_argument, 0, 'V'},
            {"help", no_argument, 0, 'h'},
            {"config", required_argument, 0, 'c'},
            {"debug", required_argument, 0, 'd'},
            {0, 0, 0, 0}
    };

    // Default log level
    logLevel = SHOW_ALL_LOGS;

    int option_index = 0;
    while ((c = getopt_long(argc, argv, "Vhi:o:a:", long_options, &option_index)) != -1) {
        switch (c) {
            case 'V': {
                this->version();
                return 0;
            }

            case 'h': {
                this->help();
                return 0;
            }

            case 'c': {
                path = optarg;
                break;
            }

            case 'd': {
                std::string logLevelOption = optarg;
                std::string validLogLevels = "APDS";
                if (validLogLevels.find(logLevelOption) != std::string::npos) {
                    logLevel = optarg;
                    break;
                } else {
                    throw "Invalid log level";
                }
            }

            default:
                std::cerr << "Unknown option '" << argv[option_index + 1] << "'" << std::endl;
                std::cerr << "Execute tp1 -h for help" << std::endl;
                return -1;
        }
    }

    return 1;
}
