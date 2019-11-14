#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdarg.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include "coriolis_lock.h"
#include "coriolis_logger.h"

// TODO: Use this???
/* Auxiliar function that creates a pretty-printeable time string. 
 * The final string is stored at str.*/
void coriolis_logger_time_string(coriolis_logger_t* ls, char* str){
	struct timeval time_now; 
	gettimeofday (&time_now, NULL);
	
	unsigned long int timestamp = (time_now.tv_sec - ls->time_created.tv_sec)*1000000L;
	timestamp += (time_now.tv_usec - ls->time_created.tv_usec);
	// Check microseconds
	if(timestamp < 1000L)
		sprintf(str, "%lu Us", timestamp);
	else if(timestamp < 1000000L) // Check miliseconds
		sprintf(str, "%.3f ms", ((double)timestamp)/1000);
	else
		sprintf(str, "%.3f s", ((double)timestamp)/1000000L);
 }

/* Opens file at route and dynamically creates a coriolis_logger
 * instance to write on it. If append is false, then the file is 
 * overwritten. Returns NULL if creating the coriolis_logger failed.*/
coriolis_logger_t* coriolis_logger_create(char* route, bool append){
	FILE *pf = fopen(route, (append ? "a" : "w"));
	if(!pf)	return NULL;
	
	coriolis_logger_t* ls = (coriolis_logger_t*) malloc(sizeof(coriolis_logger_t));
	if(!ls) {
		fclose(pf);
		return NULL;
		}
		
	ls->log_file = pf;
	
	struct timeval time_start;
	gettimeofday (&time_start, NULL);
	
	ls->time_created = time_start;
	
	ls->lock = coriolis_lock_create("coriolis_logger_log");
	if(!ls->lock) {
		fclose(pf);
		free(ls);
		return NULL;
	}
	
	return ls;
}

/* Closes the log file and destroys coriolis_logger itself.*/
void coriolis_logger_destroy(coriolis_logger_t* ls){
	if(ls && ls->log_file)
		fclose(ls->log_file);
		
	if(ls) {
		coriolis_lock_destroy(ls->lock);
		free(ls);
	}
}

/* Write string msg to coriolis_logger log file. Works exactly like 
 * printf meaning that you can pass msg as a formated string, and 
 * then specify list of arguments. If successful, returns the total
 * of characters written. Otherwise, a negative number is returned.*/
int coriolis_logger_write(char* log_line, ... ){
	coriolis_logger_t* ls = coriolis_logger_create(CORIOLIS_LOGGER_OUTPUT_FILE, true);
	if(!(ls && ls->log_file)) return -1;
		
	coriolis_lock_acquire(ls->lock);
	fflush(ls->log_file);
	
	char time_str[10];
	coriolis_logger_time_string(ls, time_str);
	
	va_list args;
	va_start(args, log_line);

	vfprintf(ls->log_file, log_line, args);
	fprintf(ls->log_file, "\n");
	va_end(args);
	fflush(ls->log_file);
	coriolis_lock_release(ls->lock);
	// TODO: Find a good way of avoiding this
	coriolis_logger_destroy(ls);
	return 0;
}

