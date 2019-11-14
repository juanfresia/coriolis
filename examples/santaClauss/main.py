import threading, time
from multiprocessing import Process, Semaphore, Value
from random import randint

REINDEER_AMOUNT = 9
ELVES_AMOUNT = 12
MIN_ELVES_FOR_HELPING = 3
SANTA_ROUNDS = 15


# @has_checkpoints
elves = 0
reindeer = 0
rounds = 0
santaSem = Semaphore(0)
reindeerSem = Semaphore(0)
elvesSem = Semaphore(0)
elfTex = Semaphore(1)
mutex = Semaphore(1)


def getHitched(reindeer_id):
    # @checkpoint get_hitched reindeer_id
    print("Reindeer {} just got hitched by Santa".format(reindeer_id))
    time.sleep(randint(1, 6) / 500.0)

def getHelp(elf_id):
    # @checkpoint get_help elf_id
    print("Elf {} just got help from Santa".format(elf_id))
    time.sleep(randint(1, 6) / 500.0)

def prepareSleigh():
    # @checkpoint prepare_sleigh
    print("Santa woke up to prepare his sleigh")
    time.sleep(randint(1, 6) / 500.0)

def helpElves():
    # @checkpoint help_elves
    print("Santa woke up to help some elves")
    time.sleep(randint(1, 6) / 500.0)

def santa_main():
    global reindeer
    global elves
    global rounds
    while rounds < SANTA_ROUNDS:
        # @checkpoint santa_sleep
        santaSem.acquire()
        # @checkpoint santa_wake
        mutex.acquire()
        rounds += 1
        if rounds >= SANTA_ROUNDS: break
        if reindeer >= REINDEER_AMOUNT:
            prepareSleigh()
            for i in range(REINDEER_AMOUNT):
                reindeerSem.release()
            reindeer -= REINDEER_AMOUNT
        elif elves >= MIN_ELVES_FOR_HELPING:
            helpElves()
            for i in range(elves):
                elvesSem.release()
        mutex.release()


    # Code to release all other threads
    mutex.release()
    for i in range(REINDEER_AMOUNT):
        reindeerSem.release()
    for i in range(ELVES_AMOUNT):
        elfTex.release()
        elvesSem.release()

def reindeer_main(reindeer_id):
    global reindeer
    global elves
    global rounds
    while rounds < SANTA_ROUNDS:
        time.sleep(randint(1, 40) / 500.0)
        # @checkpoint reindeer_arrive reindeer_id
        mutex.acquire()
        reindeer += 1
        if reindeer == REINDEER_AMOUNT:
            santaSem.release()
        mutex.release()
        reindeerSem.acquire()
        if rounds >= SANTA_ROUNDS: break
        getHitched(reindeer_id)
        # @checkpoint reindeer_leave reindeer_id

def elf_main(elf_id):
    global reindeer
    global elves
    global rounds
    while rounds < SANTA_ROUNDS:
        time.sleep(randint(1, 24) / 500.0)
        # @checkpoint elf_arrive elf_id
        elfTex.acquire()
        mutex.acquire()
        elves += 1
        if elves == MIN_ELVES_FOR_HELPING:
            santaSem.release()
        else:
            elfTex.release()
        mutex.release()
        elvesSem.acquire()
        if rounds >= SANTA_ROUNDS: break
        getHelp(elf_id)
        mutex.acquire()
        elves -= 1
        if elves == 0:
            elfTex.release()
        mutex.release()
        # @checkpoint elf_leave elf_id


if __name__ == '__main__':
    threading.Thread(target=santa_main).start()

    for i in range(ELVES_AMOUNT):
        t = threading.Thread(target=elf_main, args=(i+1,))
        t.start()

    for i in range(REINDEER_AMOUNT):
        t = threading.Thread(target=reindeer_main, args=(i+1,))
        t.start()
