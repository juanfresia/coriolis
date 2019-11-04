cmake_minimum_required(VERSION 3.14)
project(tp1)

set(CMAKE_CXX_STANDARD 14)

include_directories(./pluggins/)
include_directories(./src/)

add_executable(tp1
        pluggins/json/private/json_reader.cpp
        pluggins/json/private/json_value.cpp
        pluggins/json/private/json_tool.h
        pluggins/json/private/json_valueiterator.inl
        pluggins/json/private/json_writer.cpp
        pluggins/json/private/version.h.in
        src/Flower.h
        src/Flower.cpp
        src/ProducersManager.h
        main.cpp
        src/utils/Serializer.cpp
        src/utils/MemoryReader.cpp
        src/utils/MemoryWriter.cpp
        src/PointOfSale.cpp src/PointOfSale.h src/FlowerProducer.cpp src/FlowerProducer.h src/DistributionCenter.cpp src/DistributionCenter.h src/utils/ArgumentsProcessor.cpp src/utils/ArgumentsProcessor.h src/ProducersManager.h src/ProducersManager.cpp src/ProducersManager.h src/Concurrentes.h src/protocol/Pipe.cpp src/protocol/Pipe.h
        src/utils/ConcuMath.cpp src/utils/ConcuMath.h src/utils/GlobalConfig.cpp src/utils/GlobalConfig.h src/utils/utils.h src/utils/utils.cpp
        src/Concurrentes.h src/protocol/NamedPipe.cpp src/protocol/NamedPipe.h src/protocol/FlowerProtocol.cpp src/protocol/FlowerProtocol.h src/FlowerSimulator.cpp src/FlowerSimulator.cpp src/FlowerSimulator.h src/LogPipe.cpp src/LogPipe.h src/Logger.cpp src/Logger.h src/DistributionsManager.cpp src/DistributionsManager.h src/Flower.cpp src/PointOfSalesManager.cpp src/PointOfSalesManager.h src/ClientsManager.cpp src/ClientsManager.h src/Order.cpp src/Order.h src/Client.cpp src/Client.h)

target_link_libraries(tp1 coriolis)