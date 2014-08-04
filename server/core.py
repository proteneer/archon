from __future__ import print_function

from threading import Thread, Lock
import time
import zmq
import random

from exit import should_shutdown


class Core:

    def __init__(self):
        self.weights = None
        self._weights_lock = Lock()
        self.accrued_gradient = 0
        self._accrued_gradient_lock = Lock()
        self.context = zmq.Context()
        self.id = str(random.randint(0, 200))
        Thread(target=self._pull_weights).start()
        Thread(target=self._push_gradient).start()

    def _pull_weights(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect('tcp://localhost:5739')
        # if the shard server dies, this blocks the connection.
        while not should_shutdown():
            socket.send('i want weights!')
            # blocks
            weights = int(socket.recv())
            with self._weights_lock:
                self.weights = weights
            time.sleep(10)

    def _push_gradient(self):
        # if the shard server dies, this blocks the connection.
        while not should_shutdown():
            with self._accrued_gradient_lock:
                socket = self.context.socket(zmq.REQ)
                socket.connect('tcp://localhost:5738')
                socket.send(str(self.accrued_gradient))
                self.accrued_gradient = 0
            # blocks
            socket.recv()
            time.sleep(10)
            print('gradient sent succesfully')

    def compute_gradient(self):
        with self._accrued_gradient_lock:
            with self._weights_lock:
                print('computing gradient')
                gradient = random.randint(1,10)
                self.accrued_gradient += gradient
                time.sleep(random.randint(1, 6))
                print('finished computing expensive gradient')

    def apply_gradient(self):
        with self._accrued_gradient_lock:
            print('applying gradient')

c = Core()

while not should_shutdown():
    c.compute_gradient()
    c.apply_gradient()
    time.sleep(1)
