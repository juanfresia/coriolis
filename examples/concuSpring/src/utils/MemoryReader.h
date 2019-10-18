//
// Created by demian on 14/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_MEMORYREADER_H
#define TP1_FIUBA_CONCURRENTE_MEMORYREADER_H

#include "Serializer.h"

class MemoryReader : public Serializer {

public:
    MemoryReader(const uint8_t *buffer, size_t bufferSize);
    ~MemoryReader();

    void serialize(void *data, size_t count) override;

private:
    uint8_t* buffer;
    size_t bufferSize;
    size_t cursorPosition;
};


#endif //TP1_FIUBA_CONCURRENTE_MEMORYREADER_H
