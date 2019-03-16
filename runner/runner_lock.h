#ifndef _RUNNER_LOCK_H
#define _RUNNER_LOCK_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>

#define RUNNER_MAX_LOCK_NAME_LEN 50
#define RUNNER_LOCK_CREAT_FLAGS (O_CREAT|O_WRONLY)
#define RUNNER_LOCK_CREAT_PERMS 0777

/*
 *			LOCK Naming convention
 *
 * Every lock is stored as a file {lock_name}.runner_lock
 * 
 * 
 */

/* Lock structure to implement our own beautiful lock.*/
typedef struct _runner_lock_ {
	struct flock fl;
	int fd;
	char name[RUNNER_MAX_LOCK_NAME_LEN];
} runner_lock_t;

/* Creates a lock associated with lock_name
 * given. Returns NULL in case of error.*/
runner_lock_t* runner_lock_create(char* lock_name);

/* Sends lock to lock's heaven.*/
void runner_lock_destroy(runner_lock_t* lock);

/* Acquires the lock. If it can't be acquired, blocks
 * the current process until it can be obtained.
 * Pre: the process ain't have the lock.
 * Post: the process has the lock, and no other process
 * acquire it until this process releases it.*/
int runner_lock_acquire(runner_lock_t* lock);

/* Releases the lock, allowing other processes to
 * acquire it.
 * Pre: the process HAS the lock, and is the only
 * one with it.
 * Post: the process ain't have the lock.*/
int runner_lock_release(runner_lock_t* lock);
#endif
