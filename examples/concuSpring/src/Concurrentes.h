#ifndef CONCURRENTES_H
#define CONCURRENTES_H

#include <fstream>
#include <wait.h>
#include <iostream>
#include <memory>
#include <unistd.h>
#include <cstring>

using std::shared_ptr;

#define SIGNAL_PAUSE 'p'
#define SIGNAL_QUIT 'q'

#define FIFO_PRODUCTORS "fifo_productors"
#define FIFO_DISTRIBUTORS "fifo_distributors"
#define FIFO_SELLPOINTS "fifo_sellpoints"

#define MAX_BUFFERSIZE 1024

#define isValid(Ptr) Ptr != nullptr
#define isNotValid(Ptr) Ptr == nullptr

#endif // CONCURRENTES_H
