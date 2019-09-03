import threading, time
from multiprocessing import Condition
from random import randint

# @has_checkpoints

WRITERS_AMOUNT = 3
READERS_AMOUNT = 2
BUFFERS_AMOUNT = 1
WRITERS_ROUNDS = 3
READERS_ROUNDS = 2

def generate_random_msg(): # Just for flavour
    A = ["Wonderful", "Terrible", "Nice", "Awful", "Cool", "Pathetic", "Good", "Bad", "Lame"]
    B = ["day", "night", "experience", "dinner", "life", "code", "time", "job", "duty", "party", "meeting", "evening"]
    return A[randint(0, len(A)-1)] + "-" + B[randint(0, len(B)-1)]

class Room():
    def __init__(self, id):
        self.val = "NULL"
        self.id = id

# The class solving this problem
class RWLock:
    def __init__(self):
        self.cond = Condition()
        self.readers = 0

    def read_acquire(self):
        self.cond.acquire()
        self.readers += 1
        self.cond.release()

    def read_release(self):
        with self.cond:
            self.readers -= 1
            if (self.readers == 0):
                self.cond.notify_all()

    def write_acquire(self):
        self.cond.acquire()
        while (self.readers > 0):
            self.cond.wait()

    def write_release(self):
        self.cond.release()


def read(reader_id, locks_array, buffers_array):
    for i in range(READERS_ROUNDS):
        time.sleep(randint(1, 10) / 500.0)
        chosen = randint(0, BUFFERS_AMOUNT - 1)
        res = buffers_array[chosen]
        lock = locks_array[chosen]
        lock.read_acquire()
        print("[ R{} ] Entered room {}".format(reader_id, res.id))
        # @checkpoint reader_enter reader_id res.id
        time.sleep(randint(1,10) / 500.0)
        print("[ R{} ] Read from room {} the msg: {}".format(reader_id, res.id, res.val))
        # @checkpoint read_room reader_id res.id res.val
        time.sleep(randint(1,10) / 500.0)
        print("[ R{} ] Exited room {}".format(reader_id, res.id))
        # @checkpoint reader_exit reader_id res.id
        lock.read_release()

def write(writer_id, locks_array, buffers_array):
    for i in range(WRITERS_ROUNDS):
        time.sleep(randint(1,10) / 500.0)
        chosen = randint(0, BUFFERS_AMOUNT - 1)
        res = buffers_array[chosen]
        lock = locks_array[chosen]
        lock.write_acquire()
        print("[ W{} ] Entered room {}".format(writer_id, res.id))
        # @checkpoint writer_enter writer_id res.id
        time.sleep(randint(1,10) / 500.0)
        res.val = generate_random_msg()
        print("[ W{} ] Wrote into room {} the msg: {}".format(writer_id, res.id, res.val))
        # @checkpoint write_room writer_id res.id res.val
        time.sleep(randint(1,10) / 500.0)
        print("[ W{} ] Exited room {}".format(writer_id, res.id))
        # @checkpoint writer_exit writer_id res.id
        lock.write_release()


if __name__ == '__main__':
    locks_array = []
    buffers_array = []

    for i in range(BUFFERS_AMOUNT):
        buffers_array.append( Room(i+1) )
        locks_array.append( RWLock() )

    for i in range(READERS_AMOUNT):
        t = threading.Thread(target=read, args=(i+1, locks_array, buffers_array))
        t.start()

    for i in range(WRITERS_AMOUNT):
        t = threading.Thread(target=write, args=(i+1, locks_array, buffers_array))
        t.start()