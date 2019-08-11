#ifndef coriolis_logger_H
#define coriolis_logger_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdarg.h>
#include <sys/time.h>
#include "coriolis_lock.h"

#define CORIOLIS_LOGGER_OUTPUT_FILE "coriolis_run.log"

/* Structure used to represent coriolis_logger. */
typedef struct coriolis_logger_ {
	FILE* log_file;
	struct timeval time_created;
	coriolis_lock_t* lock;
} coriolis_logger_t;

/* Closes log file and destroys coriolis_logger itself.*/
void coriolis_logger_destroy();

/* Write string msg to coriolis_logger log file. Works exactly like 
 * printf meaning that you can pass msg as a formated string, and 
 * then specify list of arguments. If successful, returns the total
 * of characters written. Otherwise, a negative number is returned.*/
int coriolis_logger_write(char* log_line, ... );

#endif
