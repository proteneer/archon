from threading import Thread, Event, Lock
import zmq

from exit import should_shutdown

class Shard:
	def __init__(self):
		self.weights = 1234
		self._weights_lock = Lock()
		self.context = zmq.Context()
		Thread(target=self.update_core_weights).start()
		Thread(target=self.apply_gradients).start()

	def update_core_weights(self):
		socket = self.context.socket(zmq.REP)
		socket.bind('tcp://*:5739')
		# use a polling mechanism to make it non-blocking
		poller = zmq.Poller()
		poller.register(socket, zmq.POLLIN)
		while not should_shutdown():
			socks = dict(poller.poll(100))
			if socks:
				if socks.get(socket) == zmq.POLLIN:
					message = socket.recv()
					with self._weights_lock:
						socket.send(str(self.weights))

	def apply_gradients(self):
		socket = self.context.socket(zmq.REP)
		socket.bind('tcp://*:5738')
		poller = zmq.Poller()
		poller.register(socket, zmq.POLLIN)
		# use a polling mechanism to make it non-blocking
		while not should_shutdown():
			socks = dict(poller.poll(100))
			if socks:
				if socks.get(socket) == zmq.POLLIN:
					message = socket.recv()
					with self._weights_lock:
						print('server received gradient:', message)
						socket.send('OK')

s = Shard()

while not should_shutdown():
	pass
