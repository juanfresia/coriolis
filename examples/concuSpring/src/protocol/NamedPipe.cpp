#include <sys/stat.h>
#include <cstring>
#include <iostream>
#include <sys/fcntl.h>
#include <unistd.h>
#include "NamedPipe.h"

#define FIFO_PERMISSIONS 0666

NamedPipe::NamedPipe(const std::string pathname, named_pipe_type_t mode) :
    path(pathname), type(mode) {

    // First we create the named namedPipe
    if (mknod(this->path.c_str(), S_IFIFO | FIFO_PERMISSIONS, 0) < 0) {
        // We only ignore the error EEXIST
        // which means that other process
        // created the named namedPipe already
        if (errno != EEXIST) {
            std::cerr << "Could not create named pipe: " << strerror(errno) << std::endl;
            throw "Could not create named pipe";
        }
    }

    switch (this->type) {
        case NAMED_PIPE_WRITE: {
            // std::cout << "I will open the named pipe: " << this->path.c_str() << " in WRITE mode" << std::endl;
            this->fd = open(this->path.c_str(), O_WRONLY);
            break;
        }

        case NAMED_PIPE_READ: {
            // std::cout << "I will open the named pipe: " << this->path.c_str() << " in READ mode" << std::endl;
            this->fd = open(this->path.c_str(), O_RDONLY);
            break;
        }

        default:
            throw "Invalid mode for named pipe";
    }

    if (this->fd < 0) {
        std::cerr << "Could not open named pipe: " << strerror(errno) << std::endl;
        throw "Could not open named pipe";
    }
}

NamedPipe::~NamedPipe() {
    if (close(this->fd) < 0) {
        std::cerr << "Could not close named pipe: " << strerror(errno) << std::endl;
    }

    unlink(this->path.c_str());
}

int NamedPipe::readPipe(uint8_t * buf, size_t count) const {
    int s;
    int received = 0;

    if (this->type == NAMED_PIPE_WRITE) {
        throw "Could not read in write named pipe";
    }

    while (received < count) {
        s = read(this->fd, &buf[received], count - received);

        if (s < 0) {
            std::cerr << "Fail reading named pipe: " << strerror(errno) << std::endl;
            return s;
        } else if (s == 0) {
            return received;
        } else {
            received += s;
        }
    }

    return received;
}

int NamedPipe::writePipe(const uint8_t * buf, size_t count) const {
    int sent = 0;
    int s;

    if (this->type == NAMED_PIPE_READ) {
        throw "Could not write in read named pipe";
    }

    while (sent < count) {
        s = write(this->fd, &buf[sent], count - sent);

        if (s < 0) {
            std::cerr << "Fail writing named pipe: " << strerror(errno) << std::endl;
            return s;
        } else if (s == 0) {
            return sent;
        } else {
            sent += s;
        }
    }

    return s;
}
