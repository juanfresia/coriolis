#ifndef _CORIOLIS_LOCK_H
#define _CORIOLIS_LOCK_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>

#define CORIOLIS_MAX_LOCK_NAME_LEN 50
#define CORIOLIS_LOCK_CREAT_FLAGS (O_CREAT|O_WRONLY)
#define CORIOLIS_LOCK_CREAT_PERMS 0777

/*
 *			LOCK Naming convention
 *
 * Every lock is stored as a file {lock_name}.coriolis_lock
 * 
 * 
 */

/* Lock structure to implement our own beautiful lock.*/
typedef struct _coriolis_lock_ {
	struct flock fl;
	int fd;
	char name[CORIOLIS_MAX_LOCK_NAME_LEN];
} coriolis_lock_t;

/* Creates a lock associated with lock_name
 * given. Returns NULL in case of error.*/
coriolis_lock_t* coriolis_lock_create(char* lock_name);

/* Sends lock to lock's heaven.*/
void coriolis_lock_destroy(coriolis_lock_t* lock);

/* Acquires the lock. If it can't be acquired, blocks
 * the current process until it can be obtained.
 * Pre: the process ain't have the lock.
 * Post: the process has the lock, and no other process
 * acquire it until this process releases it.*/
int coriolis_lock_acquire(coriolis_lock_t* lock);

/* Releases the lock, allowing other processes to
 * acquire it.
 * Pre: the process HAS the lock, and is the only
 * one with it.
 * Post: the process ain't have the lock.*/
int coriolis_lock_release(coriolis_lock_t* lock);
#endif
