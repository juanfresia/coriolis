#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <cstring>
#include "Pipe.h"

Pipe::Pipe() {
    int descriptors[2];
    if (pipe(descriptors) < 0) {
        std::cerr << "No se pudo crear el namedPipe: " << strerror(errno) << std::endl;
    }

    this->fdread = descriptors[0];
    this->fdwrite = descriptors[1];
    this->writeable = false;
    this->readable = false;
}

Pipe::~Pipe() {
    // Only close the corresponding namedPipe
    if (this->readable) {
        close(this->fdread);
    }

    if (this->writeable) {
        close(this->fdwrite);
    }
}

int Pipe::readPipe(uint8_t * buf, size_t count) {
    int s;
    int received = 0;

    if (this->writeable) {
        throw "Could not read in write namedPipe";
    }

    if (!this->readable) {
        // This is call only once
        this->setReadable();
    }

    while (received < count) {
        s = read(this->fdread, &buf[received], count - received);

        if (s < 0) {
            std::cerr << "Fail reading unnamed pipe: " << strerror(errno) << std::endl;
            return s;
        } else if (s == 0) {
            return received;
        } else {
            received += s;
        }
    }

    return received;
}

int Pipe::writePipe(const uint8_t * buf, size_t count) {
    int sent = 0;
    int s;

    if (this->readable) {
        throw "Could not write in read unnamed pipe";
    }

    if (!this->writeable) {
        this->setWriteable();
    }

    while (sent < count) {
        s = write(fdwrite, &buf[sent], count - sent);

        if (s < 0) {
            std::cerr << "Fail writing unnamed pipe: " << strerror(errno) << std::endl;
            return s;
        } else if (s == 0) {
            return sent;
        } else {
            sent += s;
        }
    }

    return s;
}

void Pipe::setWriteable(void) {
    this->writeable = true;
    this->readable = false;

    if (close(this->fdread) < 0) {
        std::cerr << "Could not close read unnamed pipe: " << strerror(errno) << std::endl;
    }

    return;
}

void Pipe::setReadable(void) {
    this->writeable = false;
    this->readable = true;

    if (close(this->fdwrite) < 0) {
        std::cerr << "Could not close write namedPipe: " << strerror(errno) << std::endl;
    }

    return;
}