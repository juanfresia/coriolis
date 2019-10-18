//
// Created by demian on 14/9/19.
//

#include "MemoryWriter.h"

MemoryWriter::MemoryWriter() : Serializer(false) {
    this->cursorPosition = 0;
}

void MemoryWriter::serialize(void *data, size_t count) {
    memcpy(&this->buffer[cursorPosition], data, count);
    cursorPosition += count;
}



