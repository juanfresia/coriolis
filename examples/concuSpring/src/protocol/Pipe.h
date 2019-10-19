#ifndef PIPE_H
#define PIPE_H

#include <utils/types.h>

class Pipe {
    private:
        descriptor_write fdwrite;
        descriptor_read  fdread;
        bool writeable;
        bool readable;
        void setWriteable(void);
        void setReadable(void);

    public:
        Pipe();
        ~Pipe();

        int readPipe(uint8_t *, size_t);
        int writePipe(const uint8_t *, size_t);
};


#endif // PIPE_H
