//
// Created by demian on 14/9/19.
//

#include "MemoryReader.h"

MemoryReader::MemoryReader(const uint8_t *buffer, size_t bufferSize) : Serializer(true) {
    this->bufferSize = bufferSize;
    this->cursorPosition = 0;

    if(bufferSize > 0)
    {
        this->buffer = new uint8_t[bufferSize];
        memcpy(this->buffer, buffer, bufferSize);
    }
}

MemoryReader::~MemoryReader() {
    if(bufferSize > 0)
    {
        delete[] this->buffer;
    }
}

void MemoryReader::serialize(void *data, size_t count) {
    memcpy(data, &this->buffer[cursorPosition], count);
    cursorPosition += count;
}
