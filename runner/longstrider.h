#ifndef LONGSTRIDER_H
#define LONGSTRIDER_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdarg.h>
#include <sys/time.h>
#include "runner_lock.h"

#define LONGSTRIDER_OUTPUT_FILE "wonders_made_by_concu.txt"

/* Structure used to represent longstrider. */
typedef struct longstrider_ {
	FILE* log_file;
	struct timeval time_created;
	runner_lock_t* lock;
} longstrider_t;

/* Closes log file and destroys longstrider itself.*/
void longstrider_destroy();

/* Write string msg to longstrider log file. Works exactly like 
 * printf meaning that you can pass msg as a formated string, and 
 * then specify list of arguments. If successful, returns the total
 * of characters written. Otherwise, a negative number is returned.*/
int longstrider_write(char* process_type, char* checkpoint, ... );

#endif
