#ifndef LOCK_H
#define LOCK_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include "lock.h"

#define MAX_LOCK_NAME_LEN 50
#define LOCK_CREAT_FLAGS (O_CREAT|O_WRONLY)
#define LOCK_CREAT_PERMS 0777

/*
 *			LOCK Naming convention
 *
 * Every lock is stored at locks directory, in the format
 *		locks/{lock_name}.lock
 * 
 * 
 */

/* Lock structure to implement our own beautiful lock.*/
typedef struct lock_ {
	struct flock fl;
	int fd;
	char name[MAX_LOCK_NAME_LEN];
} lock_t;

/* Creates a lock associated with lock_name
 * given. Returns NULL in case of error.*/
lock_t* lock_create(char* lock_name);

/* Sends lock to lock's heaven.*/
void lock_destroy(lock_t* lock);

/* Acquires the lock. If it can't be acquired, blocks
 * the current process until it can be obtained.
 * Pre: the process ain't have the lock.
 * Post: the process has the lock, and no other process
 * acquire it until this process releases it.*/
int lock_acquire(lock_t* lock);

/* Releases the lock, allowing other processes to
 * acquire it.
 * Pre: the process HAS the lock, and is the only
 * one with it.
 * Post: the process ain't have the lock.*/
int lock_release(lock_t* lock);
#endif
