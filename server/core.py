from threading import Thread, Event, Lock
import time
import zmq
import signal
import os
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
		t = Thread(target=self._sync_weights)
		t.start()

	def _sync_weights(self):
		socket = self.context.socket(zmq.REQ)
		socket.connect('tcp://localhost:5739')
		while not should_shutdown():
			print 'syncing weights from server'
			socket.send('i want weights!')
			# use polling to make non-blocking
			weights = int(socket.recv())
			with self._weights_lock:
				self.weights = weights
				print 'weights updated successfully'
			time.sleep(1)

	def _push_gradient(self):
		with self._gradient_lock:
			print 'sending gradient...'
			socket = self.context.socket(zmq.REQ)
			socket.connect('tcp://localhost:5738')
			socket.send("client_gradient: "+self.id)
			# use polling to make non-blocking
			message = socket.recv()
			print 'gradient sent succesfully'

	def async_push_gradient(self):
		Thread(target=self._push_gradient).start()

	def compute_gradient(self):
		with self._gradient_lock:
			with self._weights_lock:
				print 'computing expensive gradient'
				time.sleep(5)
				print 'finished computing expensive gradient'

	def apply_gradient(self):
		with self._gradient_lock:
			print 'applying gradient'

c = Core()

while not should_shutdown():
	c.compute_gradient()
	c.async_push_gradient()
	c.apply_gradient()
	time.sleep(1)
