#include <utils/ArgumentsProcessor.h>
#include <FlowerSimulator.h>
#include "src/protocol/NamedPipe.h"

int main(int argc, char * argv[]) {
    ArgumentsProcessor cli;
    std::string configPath;
    std::string logLevel;

    int result = cli.processArguments(argc, argv, configPath, logLevel);

    if (result < 0) return EXIT_FAILURE;
    if (result == 0) return EXIT_SUCCESS;

    FlowerSimulator simulator(configPath, logLevel);
    simulator.start();

    return EXIT_SUCCESS;
}
