//
// Created by demian on 8/9/19.
//

#include "ConcuMath.h"
#include  <cstdlib>
#include <ctime>
#include <unistd.h>

int ConcuMath::getRandomInt(int min, int max) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    /* using nano-seconds instead of seconds */
    srand((time_t)ts.tv_nsec);
    return (rand() % (max - min + 1) + min);
}

float ConcuMath::getRandomFloat(float min, float max) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    /* using nano-seconds instead of seconds */
    srand((time_t)ts.tv_nsec);

    const float x = (float)rand()/(float)(RAND_MAX);
    return x * (max - min) + min;
}