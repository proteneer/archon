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
        self.gradient = 'hehe'
        self._gradient_lock = Lock()
        self.context = zmq.Context()
        self.id = str(random.randint(0, 200))
        t = Thread(target=self._pull_server_weights)
        t.start()

    def _pull_server_weights(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect('tcp://localhost:5739')
        while not should_shutdown():
            print('-----syncing weights from server')
            socket.send('i want weights!')
            # blocks
            weights = int(socket.recv())
            with self._weights_lock:
                self.weights = weights
                print('weights updated successfully')
            time.sleep(10)

    def _push_gradient(self):
        # if the shard server dies, this blocks the connection.
        with self._gradient_lock:
            socket = self.context.socket(zmq.REQ)
            socket.connect('tcp://localhost:5738')
            socket.send("client_gradient: "+self.gradient+" "+self.id)
        # blocks
        socket.recv()
        print('gradient sent succesfully')

    def async_push_gradient(self):
        Thread(target=self._push_gradient).start()

    def compute_gradient(self):
        with self._gradient_lock:
            with self._weights_lock:
                print('computing expensive gradient')
                time.sleep(random.randint(1, 6))
                print('finished computing expensive gradient')

    def apply_gradient(self):
        with self._gradient_lock:
            print('applying gradient')

c = Core()

while not should_shutdown():
    c.compute_gradient()
    c.async_push_gradient()
    c.apply_gradient()
    time.sleep(1)
