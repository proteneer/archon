from threading import Thread, Lock
import zmq

from exit import should_shutdown


class Shard:

    def __init__(self):
        self.weights = 1234
        self._weights_lock = Lock()
        self.context = zmq.Context()
        Thread(target=self.send_weights_to_core).start()
        Thread(target=self.apply_gradients).start()

    def send_weights_to_core(self):
        # the core can request new copies of parameters from the server
        socket = self.context.socket(zmq.REP)
        socket.bind('tcp://*:5739')
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        while not should_shutdown():
            if poller.poll(100):
                socket.recv()
                with self._weights_lock:
                    socket.send(str(self.weights))

    def apply_gradients(self):
        socket = self.context.socket(zmq.REP)
        socket.bind('tcp://*:5738')
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        while not should_shutdown():
            if poller.poll(100):
                message = socket.recv()
                with self._weights_lock:
                    print('server received gradient:', message)
                    socket.send('OK')

s = Shard()

while not should_shutdown():
    pass
