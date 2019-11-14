import threading, time
from multiprocessing import Semaphore, Value
from random import randint

# @has_checkpoints

HYDROGEN_AMOUNT = 40
OXYGEN_AMOUNT = 20


oxygen = 0
hydrogen = 0
mutex = Semaphore(1)
barrier = threading.Barrier(3)
oxyQueue = Semaphore(0)
hydroQueue = Semaphore(0)

def bond(atom_type, atom_id):
    time.sleep(randint(1, 10) / 500.0)
    # @checkpoint bond atom_type atom_id
    print("[ ID: {:02d} ] {} called bond".format(atom_id, atom_type))
    time.sleep(randint(1, 10) / 500.0)

def oxygen_main(oxy_id):
    global oxygen
    global hydrogen
    # @checkpoint atom_spawn "O" oxy_id
    time.sleep(randint(1, 12) / 500.0)
    mutex.acquire()
    oxygen += 1
    if hydrogen >= 2:
        hydroQueue.release()
        hydroQueue.release()
        hydrogen -= 2
        oxyQueue.release()
        oxygen -= 1
    else:
        mutex.release()
    oxyQueue.acquire()
    bond("O", oxy_id)
    barrier.wait()
    print("**WATER MOLECULE MADE**")
    # @checkpoint water_made
    mutex.release()
    # @checkpoint atom_die "O" oxy_id

def hydrogen_main(hydro_id):
    global oxygen
    global hydrogen
    # @checkpoint atom_spawn "H" hydro_id
    time.sleep(randint(1, 12) / 500.0)
    mutex.acquire()
    hydrogen += 1
    if hydrogen >= 2 and oxygen >= 1:
        hydroQueue.release()
        hydroQueue.release()
        hydrogen -= 2
        oxyQueue.release()
        oxygen -= 1
    else:
        mutex.release()
    hydroQueue.acquire()
    bond("H", hydro_id)
    barrier.wait()
    # @checkpoint atom_die "H" hydro_id


if __name__ == '__main__':
    for i in range(HYDROGEN_AMOUNT):
        t = threading.Thread(target=hydrogen_main, args=(i+1,))
        t.start()

    for i in range(OXYGEN_AMOUNT):
        t = threading.Thread(target=oxygen_main, args=(i+1+HYDROGEN_AMOUNT,))
        t.start()