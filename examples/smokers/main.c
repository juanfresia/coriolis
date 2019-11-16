#include <stdlib.h>
#include <signal.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#include "lock.h"
#include "semaphore.h"

// @has_checkpoints
int AGENT_ITERATIONS = 20;
int MAX_SLEEPING_TIME = 54321;

enum Semaphores {
    TOBACO_SEM = 0,
    PAPER_SEM,
    MATCHES_SEM,
    TOBACO_SIG_SEM,
    PAPER_SIG_SEM,
    MATCHES_SIG_SEM,
    AGENT_SEM,
    MEM_LOCK,
    _SEM_NUM
};

bool* table;

enum Resources {
    TOBACO = 0,
    PAPER,
    MATCHES,
    _RESOURCES_NUM
};

// Main for agent process
// Will serve randomly that many servings
void agent_main(int num_servings) {
    int semid = sem_get("main.c", _SEM_NUM);
    if (semid < 0) {
        printf("[Agent] Error getting semaphores\n");
        return;
    }

    printf("Agent started\n");
    // What it is going to serve
    unsigned int serving;
    for (int i = 0; i < AGENT_ITERATIONS; i++) {
        // @checkpoint agent_sleep
        usleep(rand() % MAX_SLEEPING_TIME);
        sem_wait(semid, AGENT_SEM);
        // @checkpoint agent_wake
        serving = rand() % 3;
        printf("Agent serving: %d\n", serving);
        // @checkpoint agent_produce serving
        sem_post(semid, serving);
        serving = (serving + 1) % 3;
        printf("Agent serving: %d\n", serving);
        // @checkpoint agent_produce serving
        sem_post(semid, serving);
    }
    sem_wait(semid, AGENT_SEM);
    exit(0);
}

void smoker_main(int resource) {
    int semid = sem_get("main.c", _SEM_NUM);
    if (semid < 0) {
        printf("[Smoker %d] Error getting semaphores\n", resource);
        return;
    }

    while(true) {
        // @checkpoint smoker_sleep resource
        usleep(rand() % MAX_SLEEPING_TIME);
        sem_wait(semid, resource + 3);
        printf("[Smoker %d] Got everything, smoking\n", resource);
        // @checkpoint smoker_take_element resource ((resource+1)%3)
        // @checkpoint smoker_take_element resource ((resource+2)%3)
        // @checkpoint smoker_smoke resource
        sem_post(semid, AGENT_SEM);
    }
    exit(0);
}

void pusher_main(int resource) {
    int semid = sem_get("main.c", _SEM_NUM);
    if (semid < 0) {
        printf("[Pusher %d] Error getting semaphores\n", resource);
        return;
    }

    int res1 = (resource + 1) % 3;
    int res2 = (resource + 2) % 3;

    while(true) {
        sem_wait(semid, resource);
        sem_wait(semid, MEM_LOCK);
        printf("[Pusher %d] Got something\n", resource);
        if (table[res1]) {
            table[res1] = false;
            sem_post(semid, res2 + 3);
        } else if (table[res2]) {
            table[res2] = false;
            sem_post(semid, res1 + 3);
        } else {
            table[resource] = true;
        }
        sem_post(semid, MEM_LOCK);
    }
    exit(0);
}

// Launches all processes and waits for them to finish
void launch() {
    printf("Spawning agent\n");
    int pid = fork();
    if(pid == 0) {
        agent_main(AGENT_ITERATIONS);
        assert(false);
    }

    for (int i = 0; i < 3; i++) {
        printf("Spawning smoker %d\n", i);
        pid = fork();
        if(pid == 0) {
            printf("I am smoker %d\n", i);
            smoker_main(i);
            assert(false);
        }
        pid = fork();
        if(pid == 0) {
            printf("I am pusher %d\n", i);
            pusher_main(i);
            assert(false);
        }
    }
}

// Create concurrency resources
// - one array of semaphores containing all the once needed
void init(bool** table_store) {
    srand(time(NULL));

    int semid;
    semid = sem_get("main.c", _SEM_NUM);
    sem_init(semid, AGENT_SEM, 1);
    sem_init(semid, TOBACO_SEM, 0);
    sem_init(semid, PAPER_SEM, 0);
    sem_init(semid, MATCHES_SEM, 0);
    sem_init(semid, TOBACO_SIG_SEM, 0);
    sem_init(semid, PAPER_SIG_SEM, 0);
    sem_init(semid, MATCHES_SIG_SEM, 0);
    sem_init(semid, MEM_LOCK, 1);

}

// Clean concurrency resources
void clean() {
    int semid = sem_get("main.c", _SEM_NUM);
    sem_destroy(semid);

}


void main() {
    srand(time(NULL));
    key_t key = ftok("main.c", 6);
    int shmid = shmget(key, sizeof(bool) * _RESOURCES_NUM, IPC_CREAT | 0644);
    table = shmat(shmid, NULL, 0);
    for (int i = 0; i < _RESOURCES_NUM; i++) {
        table[i] = false;
    }

    init(&table);
    launch();

    wait(NULL);
    kill(-1, 9);
    clean();
    shmdt(table);
    return;
}
