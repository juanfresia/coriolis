
#ifndef NAMED_PIPE__H
#define NAMED_PIPE__H


#include <string>
#include <utils/types.h>


class NamedPipe {
    private:
        std::string path;
        named_pipe_type_t type;
        int fd;

    public:
        NamedPipe(std::string, named_pipe_type_t);
        virtual ~NamedPipe();

        int readPipe(uint8_t *, size_t) const;
        int writePipe(const uint8_t *, size_t) const;
};


#endif // NAMED_PIPE__H
