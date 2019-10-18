//
// Created by demian on 14/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_MEMORYWRITER_H
#define TP1_FIUBA_CONCURRENTE_MEMORYWRITER_H

#include "Serializer.h"



class MemoryWriter : public Serializer {

public:

    MemoryWriter();

    virtual ~MemoryWriter() {}

    inline uint8_t* getBuffer() { return buffer; }
    inline size_t getBufferSize() const { return cursorPosition;}

    virtual void serialize(void *data, size_t count) override;

protected:
    uint8_t buffer[MAX_BUFFERSIZE];

    size_t cursorPosition;
};


#endif //TP1_FIUBA_CONCURRENTE_MEMORYWRITER_H
